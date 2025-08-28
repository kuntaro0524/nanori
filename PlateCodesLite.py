#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PlateCodesLite
==============
A pandas-free version of PlateCodes that avoids importing pandas/pyarrow.
Uses only Python stdlib + NumPy.

API:
  pc = PlateCodesLite(anchors, params=None)
  pc.getCodes("A7") -> (SX_pulse, Y1_pulse)
  pc.to_csv("plate_codes.csv")  # writes all wells (A..H x 1..12)

Anchors: dict like {"A1": (sx, y1), "H1": (...), "A7": (...)}
Params: set geometry if needed (offset, pitch, sizes).
"""

from dataclasses import dataclass
from typing import Dict, Tuple, Optional, List
import re
import csv
import math
import numpy as np

@dataclass
class PlateParams:
    n_rows: int = 8
    n_cols: int = 12
    pitch_x_mm: float = 9.0
    pitch_y_mm: float = 9.0
    offset_x_mm: float = 5.5
    offset_y_mm: float = 5.5
    pulses_per_mm: float = 250.0  # informational only

def _parse_well_label(well: str) -> Tuple[int, int]:
    s = str(well).strip().upper()
    m = re.match(r'^([A-Z])\s*([0-9]+)$', s)
    if not m:
        raise ValueError(f"Invalid well label: {well}")
    row_letter, col_str = m.groups()
    row_idx = ord(row_letter) - ord('A') + 1
    col_idx = int(col_str)
    return row_idx, col_idx

def _well_label(row_idx: int, col_idx: int) -> str:
    return f"{chr(ord('A') + row_idx - 1)}{col_idx}"

def _well_mm(row_idx: int, col_idx: int, P: PlateParams) -> Tuple[float, float]:
    x = P.offset_x_mm + P.pitch_x_mm * (col_idx - 1)
    y = P.offset_y_mm + P.pitch_y_mm * (row_idx - 1)
    return x, y

def _triangle_area2(p, q, r) -> float:
    return (q[0]-p[0])*(r[1]-p[1]) - (q[1]-p[1])*(r[0]-p[0])

def _fit_affine_2d(src_xy: np.ndarray, dst_uv: np.ndarray) -> np.ndarray:
    N = src_xy.shape[0]
    X = np.hstack([src_xy, np.ones((N,1))])
    U = dst_uv[:,0:1]
    V = dst_uv[:,1:2]
    Au, *_ = np.linalg.lstsq(X, U, rcond=None)
    Av, *_ = np.linalg.lstsq(X, V, rcond=None)
    return np.vstack([Au.T, Av.T])  # 2x3

class PlateCodesLite:
    def __init__(self, anchors: Dict[str, Tuple[float, float]], params: Optional[PlateParams] = None):
        self.params = params or PlateParams()
        if len(anchors) != 3:
            raise ValueError("Provide exactly 3 anchor wells in 'anchors'.")
        # Normalize anchors
        self.anchors = {str(k).strip().upper(): (float(v[0]), float(v[1])) for k, v in anchors.items()}
        # Build fit
        src_pts = []
        dst_pts = []
        for w, (sx, y1) in self.anchors.items():
            r, c = _parse_well_label(w)
            if not (1 <= r <= self.params.n_rows and 1 <= c <= self.params.n_cols):
                raise ValueError(f"Anchor '{w}' is out of bounds {self.params.n_rows}x{self.params.n_cols}.")
            x_mm, y_mm = _well_mm(r, c, self.params)
            src_pts.append([x_mm, y_mm])
            dst_pts.append([sx, y1])
        self.src_mm = np.asarray(src_pts, dtype=float)
        self.dst_pulse = np.asarray(dst_pts, dtype=float)
        area2 = _triangle_area2(self.src_mm[0], self.src_mm[1], self.src_mm[2])
        if abs(area2) < 1e-9:
            raise ValueError("The three anchor wells are collinear; affine fit is ill-posed.")
        self.A = _fit_affine_2d(self.src_mm, self.dst_pulse)
        # build map
        self._build_table()

    def _apply_affine(self, xy: np.ndarray) -> np.ndarray:
        xy1 = np.hstack([xy, np.ones((xy.shape[0],1))])
        return xy1 @ self.A.T

    def _build_table(self):
        self._rows: List[dict] = []
        self._map: Dict[str, Tuple[float,float]] = {}
        for r in range(1, self.params.n_rows+1):
            for c in range(1, self.params.n_cols+1):
                x_mm, y_mm = _well_mm(r, c, self.params)
                sx, y1 = self._apply_affine(np.array([[x_mm, y_mm]]))[0]
                well = _well_label(r, c)
                rec = {
                    "well": well,
                    "row": chr(ord('A') + r - 1),
                    "col": c,
                    "X_mm": round(float(x_mm), 4),
                    "Y_mm": round(float(y_mm), 4),
                    "SX_pulse": float(sx),
                    "Y1_pulse": float(y1),
                }
                self._rows.append(rec)
                self._map[well] = (float(sx), float(y1))

    def getCodes(self, well: str) -> Tuple[float, float]:
        key = str(well).strip().upper()
        if key not in self._map:
            r, c = _parse_well_label(key)  # may raise helpful error
            if not (1 <= r <= self.params.n_rows and 1 <= c <= self.params.n_cols):
                raise KeyError(f"Well {key} out of bounds {self.params.n_rows}x{self.params.n_cols}.")
            raise KeyError(f"Well {key} not found (unexpected).")
        return self._map[key]

    def to_csv(self, path: str):
        fieldnames = ["well","row","col","X_mm","Y_mm","SX_pulse","Y1_pulse"]
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for rec in self._rows:
                w.writerow(rec)

    def anchor_fit_report_rows(self) -> List[dict]:
        rows = []
        for w, (sx_meas, y1_meas) in self.anchors.items():
            r, c = _parse_well_label(w)
            x_mm, y_mm = _well_mm(r, c, self.params)
            sx_fit, y1_fit = self._apply_affine(np.array([[x_mm, y_mm]]))[0]
            rows.append({
                "well": w,
                "X_mm": float(x_mm), "Y_mm": float(y_mm),
                "SX_meas": float(sx_meas), "Y1_meas": float(y1_meas),
                "SX_fit": float(sx_fit), "Y1_fit": float(y1_fit),
                "SX_resid": float(sx_meas - sx_fit), "Y1_resid": float(y1_meas - y1_fit),
            })
        return rows

if __name__ == "__main__":
    # Demo with your example anchors
    anchors = {"A1": (6760, 20930), "H1": (6760, 36680), "A7": (20260, 36680)}
    pc = PlateCodesLite(anchors=anchors)
    # A1, B1, C1, ..., H1   
    for r in range(1, 9):
        well = _well_label(r, 2)
        sx, y1 = pc.getCodes(well)
        print(f"{well}: SX={sx:.1f}, Y1={y1:.1f}")

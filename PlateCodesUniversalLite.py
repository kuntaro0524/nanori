#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PlateCodesUniversalLite
-----------------------
3点アンカー（例: A1, H1, A7）の機械座標 (SX, Y1) から、8x12（A..H x 1..12）の
全ウェル座標を計算します。pandas不要、NumPyのみ。

モード:
- mode="affine": 2Dアフィン（平行移動＋回転＋異方スケール＋せん断）。非直交も可。
  * 3点が同一直線上でないこと。
  * 3点アンカーは厳密一致（残差ほぼ0）。
- mode="aligned": 軸整合（SXは列のみ、Y1は行のみの関数）。
  * 与えた3点に「同一列で行違い」の組と「同行で列違い」の組が含まれる必要あり
    （例: A1/H1 と A1/A7）。

使い方(例):
    anchors = {"A1": (6760, 20930), "H1": (6760, 36680), "A7": (20260, 36680)}
    pc = PlateCodesUniversalLite(anchors, mode="affine")
    print(pc.getCodes("A2"))
    pc.to_csv("plate_codes.csv")
"""

from dataclasses import dataclass
from typing import Dict, Tuple, Optional, List
import re
import csv
import numpy as np
import sys

@dataclass
class PlateParams:
    n_rows: int = 8
    n_cols: int = 12
    pitch_x_mm: float = 9.0
    pitch_y_mm: float = 9.0
    offset_x_mm: float = 5.5
    offset_y_mm: float = 5.5
    pulses_per_mm: float = 250.0  # 2mm=500pulse -> 1mm=250pulse（情報用）


def _parse_well_label(well: str):
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


def _well_mm(r: int, c: int, P: PlateParams):
    # 図面(mm)座標: xが列方向(1..n_cols), yが行方向(A..H)
    x = P.offset_x_mm + P.pitch_x_mm * (c - 1)
    y = P.offset_y_mm + P.pitch_y_mm * (r - 1)
    return x, y


def _triangle_area2(p, q, r) -> float:
    # 三角形pqrの符号付き面積×2（共線チェック用）
    return (q[0]-p[0])*(r[1]-p[1]) - (q[1]-p[1])*(r[0]-p[0])


def _fit_affine_2d(src_xy: np.ndarray, dst_uv: np.ndarray) -> np.ndarray:
    # src(N,2) -> dst(N,2) の2Dアフィン（最小二乗）を推定。返り値は(2x3)行列A
    N = src_xy.shape[0]
    X = np.hstack([src_xy, np.ones((N, 1))])  # (N,3)
    U = dst_uv[:, 0:1]
    V = dst_uv[:, 1:2]
    Au, *_ = np.linalg.lstsq(X, U, rcond=None)
    Av, *_ = np.linalg.lstsq(X, V, rcond=None)
    return np.vstack([Au.T, Av.T])  # [[a b c],[d e f]]

class PlateCodesUniversalLite:
    def __init__(self, anchors: Dict[str, Tuple[float, float]], mode: str = "affine",
                 params: Optional[PlateParams] = None):
        self.params = params or PlateParams()
        self.mode = mode.lower().strip()
        if len(anchors) != 3:
            raise ValueError("Provide exactly 3 anchors.")
        # アンカー正規化
        self.anchors = {str(k).strip().upper(): (float(v[0]), float(v[1])) for k, v in anchors.items()}
        # アンカーの index と 図面(mm)座標を準備
        info = []
        for w, (sx, y1) in self.anchors.items():
            r, c = _parse_well_label(w)
            x_mm, y_mm = _well_mm(r, c, self.params)
            info.append((w, r, c, sx, y1, x_mm, y_mm))
        self.info = info

        # モード別フィット
        if self.mode == "affine":
            self._fit_affine()
        elif self.mode == "aligned":
            self._fit_aligned()
        else:
            raise ValueError("mode must be 'affine' or 'aligned'")

        # 全テーブル構築
        self._build_table()

    # ------- アフィン版 -------
    def _fit_affine(self):
        src = np.array([[x_mm, y_mm] for (_, _, _, _, _, x_mm, y_mm) in self.info], dtype=float)
        dst = np.array([[sx, y1]     for (_, _, _, sx, y1, _, _) in self.info], dtype=float)
        if abs(_triangle_area2(src[0], src[1], src[2])) < 1e-9:
            raise ValueError("Three anchors are collinear; affine fit ill-posed.")
        self.A = _fit_affine_2d(src, dst)  # 2x3
        # aligned用パラメータは None のまま
        self.du = self.u0 = self.dv = self.v0 = None

    # ------- 軸整合版 -------
    def _fit_aligned(self):
        info = self.info
        dv = None; v0 = None
        du = None; u0 = None
        for i in range(3):
            for j in range(i+1, 3):
                wi, ri, ci, sxi, y1i, _, _ = info[i]
                wj, rj, cj, sxj, y1j, _, _ = info[j]
                # 同一列で行違い → 行ピッチ dv, 原点Y v0
                if ci == cj and ri != rj:
                    dv = (y1j - y1i) / (rj - ri)
                    v0 = y1i - (ri - 1) * dv
                # 同一行で列違い → 列ピッチ du, 原点X u0
                if ri == rj and ci != cj:
                    du = (sxj - sxi) / (cj - ci)
                    u0 = sxi - (ci - 1) * du
        if dv is None or v0 is None:
            raise ValueError("Need two anchors with SAME COLUMN & different ROWS (e.g., A1/H1).")
        if du is None or u0 is None:
            raise ValueError("Need two anchors with SAME ROW & different COLUMNS (e.g., A1/A7).")
        self.du, self.u0 = du, u0
        self.dv, self.v0 = dv, v0
        # affine用Aは使わない
        self.A = None

    def _apply(self, x_mm, y_mm, r, c):
        if self.mode == "affine":
            xy1 = np.array([x_mm, y_mm, 1.0])
            u, v = (self.A @ xy1)
            return float(u), float(v)
        else:  # aligned
            u = self.u0 + (c - 1) * self.du
            v = self.v0 + (r - 1) * self.dv
            return float(u), float(v)

    def _build_table(self):
        self._rows: List[dict] = []
        self._map: Dict[str, Tuple[float, float]] = {}
        for r in range(1, self.params.n_rows + 1):
            for c in range(1, self.params.n_cols + 1):
                x_mm, y_mm = _well_mm(r, c, self.params)
                u, v = self._apply(x_mm, y_mm, r, c)
                well = _well_label(r, c)
                rec = {
                    "well": well,
                    "row": chr(ord('A') + r - 1),
                    "col": c,
                    "X_mm": round(float(x_mm), 4),
                    "Y_mm": round(float(y_mm), 4),
                    "SX_pulse": float(u),
                    "Y1_pulse": float(v),
                }
                self._rows.append(rec)
                self._map[well] = (float(u), float(v))

    def getCodes(self, well: str) -> Tuple[float, float]:
        key = str(well).strip().upper()
        if key not in self._map:
            r, c = _parse_well_label(key)  # エラーメッセージ改善用
            if not (1 <= r <= self.params.n_rows and 1 <= c <= self.params.n_cols):
                raise KeyError(f"Well {key} out of bounds {self.params.n_rows}x{self.params.n_cols}.")
            raise KeyError(f"Well {key} not found.")
        return self._map[key]

    def to_csv(self, path: str):
        fields = ["well", "row", "col", "X_mm", "Y_mm", "SX_pulse", "Y1_pulse"]
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for rec in self._rows:
                w.writerow(rec)

    def anchor_residuals(self) -> List[dict]:
        """3アンカーの再現値と残差（Sanity check）。"""
        rows = []
        for w, (sx_meas, y1_meas) in self.anchors.items():
            r, c = _parse_well_label(w)
            x_mm, y_mm = _well_mm(r, c, self.params)
            u, v = self._apply(x_mm, y_mm, r, c)
            rows.append({
                "well": w, "SX_meas": sx_meas, "Y1_meas": y1_meas,
                "SX_fit": u, "Y1_fit": v,
                "SX_resid": sx_meas - u, "Y1_resid": y1_meas - v
            })
        return rows


if __name__ == "__main__":
    # 簡単デモ
    #anchors = {"A1": (6760, 21030), "H1": (6760, 36780), "A7": (20260, 21030)}
    anchors = {"A1": (6550, 21780), "H1": (7100, 37530), "A7": (20050, 21330)}

    # 1) 非直交OK（アフィン）
    pc_aff = PlateCodesUniversalLite(anchors, mode="affine")
    values = pc_aff.getCodes(sys.argv[1])
    print(f"AFFINE {sys.argv[1]}: {values[0]:.1f}, {values[1]:.1f}")
    #print("AFFINE residuals:", pc_aff.anchor_residuals())

    # 2) 行=Y/列=X を厳密維持（軸整合）
    #pc_aln = PlateCodesUniversalLite(anchors, mode="aligned")
    #print("ALIGNED A2:", pc_aln.getCodes("A2"))
    #print("ALIGNED residuals:", pc_aln.anchor_residuals())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
From three anchors (A1, H1, A7) in machine pulses, compute the stage target map
for wells A-H (horizontal) and 1-7 (vertical).

Assumptions:
- Horizontal axis = A..H (rows 1..8), Vertical axis = 1..N (columns).
- Machine axes: S-X corresponds to 1..N direction; Y1 corresponds to A..H direction.
- Axis-aligned (no skew): u = u0 + (col-1)*du, v = v0 + (row-1)*dv
- 2 mm = 500 pulse (1 mm = 250 pulse) used only for reporting.

Usage:
  python make_stage_map_A1_H1_A7.py --A1 6760 20930 --H1 6760 36680 --A7 20260 36680 --out map.csv
  or
  python make_stage_map_A1_H1_A7.py --calib anchors.csv --out map.csv
  仕様・前提

座標系：
水平（短手）= A→H（row 1..8）→ Y1 が増加
垂直（長手）= 1→N（col 1..N）→ S-X が増加
計算モデル（軸平行、相対のみ）
列方向ピッチ（pulse）: du = (SX_A7 − SX_A1) / (7 − 1)
行方向ピッチ（pulse）: dv = (Y1_H1 − Y1_A1) / (8 − 1)
原点（A1）: u0 = SX_A1, v0 = Y1_A1
任意ウェル (row=r, col=c) の目標：
SX = u0 + (c−1)*du
Y1 = v0 + (r−1)*dv
参考：2 mm = 500 pulse（1 mm = 250 pulse）を報告用に併記（計算そのものは pulse ベース）
必要であれば、1–12 までや全 96 ウェル版の出力、あるいは**アフィン変換（回転・せん断含む）**を使う高精度版にも対応します。
"""

import argparse
import pandas as pd

def parse_args():
    ap = argparse.ArgumentParser(description="Compute stage map (pulses) from A1,H1,A7 anchors.")
    ap.add_argument("--A1", nargs=2, type=float, help="S-X, Y1 pulses for A1")
    ap.add_argument("--H1", nargs=2, type=float, help="S-X, Y1 pulses for H1")
    ap.add_argument("--A7", nargs=2, type=float, help="S-X, Y1 pulses for A7")
    ap.add_argument("--calib", help="CSV file with columns well,SX_pulse,Y1_pulse for A1,H1,A7")
    ap.add_argument("--out", required=True, help="Output CSV path")
    ap.add_argument("--nrows", type=int, default=8, help="Number of rows (A..), default 8")
    ap.add_argument("--ncols", type=int, default=7, help="Number of columns (1..), default 7")
    return ap.parse_args()

def load_calib(args):
    if args.calib:
        df = pd.read_csv(args.calib)
        need = {"A1","H1","A7"}
        got = set(df["well"].astype(str).str.upper().str.strip())
        if got != need:
            raise SystemExit(f"Calibration CSV must contain exactly {sorted(need)}; got {sorted(got)}")
        df = df.set_index(df["well"].astype(str).str.upper().str.strip())
        A1 = (float(df.loc["A1","SX_pulse"]), float(df.loc["A1","Y1_pulse"]))
        H1 = (float(df.loc["H1","SX_pulse"]), float(df.loc["H1","Y1_pulse"]))
        A7 = (float(df.loc["A7","SX_pulse"]), float(df.loc["A7","Y1_pulse"]))
        return A1, H1, A7
    else:
        if not (args.A1 and args.H1 and args.A7):
            raise SystemExit("Provide either --calib CSV or all of --A1, --H1, --A7.")
        return tuple(args.A1), tuple(args.H1), tuple(args.A7)

def row_label(i):  # 1->'A'
    return chr(ord('A') + i - 1)

def main():
    args = parse_args()
    (u_A1, v_A1), (u_H1, v_H1), (u_A7, v_A7) = load_calib(args)

    # Step sizes
    du = 0.0 if args.ncols==1 else (u_A7 - u_A1) / (7 - 1)  # col pitch from 1->7
    dv = 0.0 if args.nrows==1 else (v_H1 - v_A1) / (8 - 1)  # row pitch from A->H
    u0, v0 = u_A1, v_A1  # origin at A1

    rows = []
    for r in range(1, args.nrows+1):           # A..H
        for c in range(1, args.ncols+1):       # 1..7
            u = u0 + (c-1)*du   # S-X
            v = v0 + (r-1)*dv   # Y1
            rows.append({
                "well": f"{row_label(r)}{c}",
                "row": row_label(r),
                "col": c,
                "SX_pulse": round(u, 3),
                "Y1_pulse": round(v, 3)
            })
    df = pd.DataFrame(rows, columns=["well","row","col","SX_pulse","Y1_pulse"])
    df.to_csv(args.out, index=False)

    pulses_per_mm = 250.0
    print(f"du (col pitch): {du:.3f} pulse (~{du/pulses_per_mm:.3f} mm)")
    print(f"dv (row pitch): {dv:.3f} pulse (~{dv/pulses_per_mm:.3f} mm)")
    print(f"A1 origin: SX={u0:.3f}, Y1={v0:.3f}")
    print('OK')

if __name__ == "__main__":
    main()

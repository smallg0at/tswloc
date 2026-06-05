#!/usr/bin/env python3
"""列出 CSV 文件中重复的 `key` 值及计数。"""
import sys
import argparse
import pandas as pd


def main():
    p = argparse.ArgumentParser()
    p.add_argument("file", help="CSV file path")
    p.add_argument("--min", type=int, default=2, help="最小重复次数 (默认 2)")
    p.add_argument("--out", help="将结果写入文件 (可选)")
    args = p.parse_args()

    df = pd.read_csv(args.file, dtype=str).fillna("")
    counts = df['key'].value_counts()
    dups = counts[counts >= args.min]
    print(f"file={args.file}, total_rows={len(df)}, duplicate_key_count={len(dups)}")
    if len(dups) == 0:
        return

    if args.out:
        dups.to_csv(args.out, header=['count'])
        print(f"Wrote duplicate list to: {args.out}")
    else:
        for k, c in dups.items():
            print(f"{k}\t{c}")


if __name__ == '__main__':
    main()

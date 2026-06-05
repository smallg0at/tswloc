import csv
import sys
from collections import defaultdict

def fix_tbt(input_path, output_path=None):

    with open(input_path, newline='', encoding='utf-8') as f:
        reader = list(csv.reader(f))

    if not reader:
        print('empty file')
        return

    # Treat first row as header if any non-empty string in first row contains non-numeric values
    header = None
    rows = reader
    # build map from second column value to list of rows
    map_by_col2 = defaultdict(list)
    for r in rows:
        if len(r) >= 2:
            map_by_col2[r[1]].append(r)

    out_rows = []
    for r in rows:
        if len(r) >= 3 and r[2] == 'TBT':
            candidates = [c for c in map_by_col2.get(r[1], []) if c is not r and (len(c) < 3 or c[2] != 'TBT')]
            if candidates:
                # choose first non-TBT candidate and use it to override this row
                replacement = candidates[0]
                # preserve the original key value when replacing to avoid creating duplicate keys
                new_row = replacement.copy()
                if len(r) >= 1 and len(new_row) >= 1:
                    new_row[0] = r[0]
                out_rows.append(new_row)
                continue
        out_rows.append(r)

    target_path = output_path if output_path else input_path
    with open(target_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(out_rows)

    print(f'Wrote fixed CSV to: {target_path}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python reprocess.py input.csv [output.csv]')
        sys.exit(1)
    inp = sys.argv[1]
    outp = sys.argv[2] if len(sys.argv) > 2 else None
    fix_tbt(inp, outp)

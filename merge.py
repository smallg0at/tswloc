import csv
import sys

def merge_csvs(file1, file2, output):
    # Read second file into a dictionary
    lookup = {}
    with open(file2, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 3:
                lookup[row[0]] = row[2]

    # Process first file and write output
    with open(file1, 'r', encoding='utf-8') as f_in, \
         open(output, 'w', newline='', encoding='utf-8') as f_out:
        reader = csv.reader(f_in)
        writer = csv.writer(f_out)

        for row in reader:
            if len(row) >= 1:
                key = row[0]
                value = lookup.get(key, "TBT")
                if value == "TBT":
                    print(key)
                if len(row) >= 3:
                    row[2] = value
                else:
                    row.append(value)
            writer.writerow(row)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python merge.py <file1.csv> <file2.csv> <output.csv>")
        sys.exit(1)

    merge_csvs(sys.argv[1], sys.argv[2], sys.argv[3])
    print(f"Merged CSV saved to {sys.argv[3]}")
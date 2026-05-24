import csv
import sys
from pathlib import Path


def split_dataset(input_file: str, num_parts: int = 2):
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)

    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        headers = reader.fieldnames

    total_rows = len(rows)
    rows_per_part = total_rows // num_parts

    print(f"Splitting {total_rows} rows into {num_parts} parts (~{rows_per_part} rows each)")

    output_dir = input_path.parent / 'split'
    output_dir.mkdir(exist_ok=True)

    for i in range(num_parts):
        start_idx = i * rows_per_part
        end_idx = start_idx + rows_per_part if i < num_parts - 1 else total_rows

        part_rows = rows[start_idx:end_idx]
        output_file = output_dir / f"{input_path.stem}_part{i+1}{input_path.suffix}"

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(part_rows)

        print(f"  Part {i+1}: {len(part_rows)} rows -> {output_file}")

    print(f"\nDone! Files saved to {output_dir}/")


if __name__ == "__main__":
    num_parts = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    input_file = sys.argv[2] if len(sys.argv) > 2 else "datasets/lifestyle_progresspics.csv"

    split_dataset(input_file, num_parts)

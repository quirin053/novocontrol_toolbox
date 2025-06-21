import argparse
import random
import sys

def parse_file(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    header_lines = []
    data_start = 0
    for i, line in enumerate(lines):
        if line.strip() and line.strip()[0].isdigit():
            data_start = i
            break
        header_lines.append(line.rstrip())

    column_names = header_lines[-1].split('\t')
    data_lines = lines[data_start:]
    data = [list(map(float, line.strip().split())) for line in data_lines]

    return header_lines, column_names, data

def resolve_excluded_columns(column_names, exclude_patterns):
    exclude_patterns = [p.lower() for p in exclude_patterns]
    matched_columns = [name for name in column_names
                        if any(p in name.lower() for p in exclude_patterns)]
    
    if matched_columns:
        print("Excluded columns based on pattern match:")
        for name in matched_columns:
            print(f'  "{name}"')
    else:
        print("No columns matched the exclude patterns.")
    
    return matched_columns

def scramble_data(data, column_names, exclude_columns):
    indices_to_scramble = [
        i for i, name in enumerate(column_names) if name not in exclude_columns
    ]

    if not indices_to_scramble:
        print("Nothing to scramble. Exiting.")
        sys.exit(0)

    global_factor = random.uniform(0.5, 2.0)

    scrambled_data = []
    for row in data:
        new_row = []
        for i, val in enumerate(row):
            if i in indices_to_scramble:
                individual_factor = random.uniform(0.8, 1.2)
                new_val = val * global_factor * individual_factor
                new_row.append(new_val)
            else:
                new_row.append(val)
        scrambled_data.append(new_row)

    return scrambled_data

def write_scrambled_file(filepath, header_lines, column_names, scrambled_data):
    if filepath.lower().endswith('.txt'):
        output_file = filepath[:-4] + '_scrambled.txt'
    else:
        output_file = filepath + '_scrambled.txt'
    with open(output_file, 'w') as file:
        for line in header_lines[:-1]:
            file.write(line + '\n')
        file.write('\t'.join(column_names) + '\n')
        for row in scrambled_data:
            file.write('\t'.join(f'{val:.5e}' for val in row) + '\n')

    print(f"\nScrambled data written to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Scramble measurement file.")
    parser.add_argument('file', help="Path to the measurement .txt file.")
    parser.add_argument('--exclude', nargs='*', default=[],
                        help='Column name patterns to exclude (partial match, case-insensitive).')
    parser.add_argument('--list-columns', action='store_true',
                        help='List available column headers and exit.')

    args = parser.parse_args()

    header_lines, column_names, data = parse_file(args.file)

    if args.list_columns:
        print("Available column headers:")
        for name in column_names:
            print(f'  "{name}"')
        sys.exit(0)

    if args.exclude:
        exclude_columns = resolve_excluded_columns(column_names, args.exclude)
    else:
        print("No columns excluded from scrambling!")
        print("Example usage to exclude frequency: --exclude freq")
        confirm = input("Are you sure you want to scramble ALL columns? [y/N]: ")
        if confirm.strip().lower() != 'y':
            print("Aborted.")
            sys.exit(0)
        exclude_columns = []

    scrambled_data = scramble_data(data, column_names, exclude_columns)
    write_scrambled_file(args.file, header_lines, column_names, scrambled_data)

if __name__ == '__main__':
    main()

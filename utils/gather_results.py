import os
import pandas as pd
import numpy as np
import argparse

def gather_results(output_dir, format_float=False):
    data = []

    # Walk through subdirectories
    for subdir, _, files in os.walk(output_dir):
        if 'vggt_results.txt' in files:
            result_path = os.path.join(subdir, 'vggt_results.txt')
            with open(result_path, 'r') as f:
                lines = f.readlines()
                metrics = {}
                for line in lines:
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        try:
                            metrics[key.strip()] = float(value.strip())
                        except ValueError:
                            metrics[key.strip()] = value.strip()
                metrics['folder'] = os.path.basename(subdir)
                data.append(metrics)

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Reorder columns to have 'folder' first
    cols = ['folder'] + [col for col in df.columns if col != 'folder']
    df = df[cols]

    # Compute average and std for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    avg_row = {col: df[col].mean() for col in numeric_cols}
    std_row = {col: df[col].std() for col in numeric_cols}
    avg_row['folder'] = 'AVERAGE'
    std_row['folder'] = 'STD'

    # Sort the main data rows by folder name
    df_sorted = df.sort_values(by='folder', key=lambda col: col.str.lower())

    # Append summary rows
    df_final = pd.concat([df_sorted, pd.DataFrame([avg_row, std_row])], ignore_index=True)
    df_final = df_final[cols]  # Ensure column order

    # Apply float formatting to 4 significant digits if requested
    if format_float:
        df_final[numeric_cols] = df_final[numeric_cols].applymap(lambda x: float(f"{x:.4g}") if pd.notnull(x) else x)

    # Save to CSV in the output_dir
    output_csv = os.path.join(output_dir, 'aggregated_results.csv')
    df_final.to_csv(output_csv, index=False)
    print(f"Saved aggregated results with summary to {output_csv}")

# Use argparse to pass in output_dir
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Aggregate results from results.txt files.')
    parser.add_argument('output_dir', type=str, help='Directory containing subfolders with results.txt files')
    parser.add_argument('--format_float', action='store_true', help='Format floating numbers to 4 significant digits')
    args = parser.parse_args()

    gather_results(args.output_dir, format_float=args.format_float)
import pandas as pd
import numpy as np
import re
import argparse
import csv
import shutil
import os
from collections import defaultdict

def convert_txt_to_csv(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            # Replace tabs with commas
            csv_line = line.replace('\t', ',')
            outfile.write(csv_line)


def process_benchmark_results_tp(log_filename_base, iterations, output_csv_filename):
    # Function to parse the log file and extract benchmarking data
    def parse_log_file(filename):
        operations_data = defaultdict(lambda: {
            'PAPI instructions': [],
            'PAPI cycles': [],
            'IPC': [],
            'Overall throughput': [],
            'Operation time': []
        })
        current_iteration = None
        current_operation = None

        with open(log_filename_base, 'r') as file:
            lines = file.readlines()

            for line in lines:
                line = line.strip()

                # Check for iteration number
                if line.startswith('Starting iteration'):
                    parts = line.split()
                    current_iteration = int(parts[2])  # Assuming 'Starting iteration X of Y' format
                    continue

                # Check for operation type after "Doing"
                if line.startswith('Doing'):
                    current_operation = line.split('Doing ')[1].strip()
                    continue

                # Extract data after finding the operation type and iteration number
                if current_iteration is not None and current_operation is not None:
                    if line.startswith('PAPI instructions'):
                        papi_instructions = int(line.split(':')[1].strip())
                        operations_data[current_operation]['PAPI instructions'].append(papi_instructions)
                    elif line.startswith('PAPI cycles'):
                        papi_cycles = int(line.split(':')[1].strip())
                        operations_data[current_operation]['PAPI cycles'].append(papi_cycles)
                    elif line.startswith('IPC'):
                        ipc = float(line.split(':')[1].strip())
                        operations_data[current_operation]['IPC'].append(ipc)
                    elif line.startswith('Overall throughput'):
                        # Extract numeric value using regular expression
                        overall_throughput_match = re.search(r'\d+(?:\.\d+)?(?:[eE][+-]?\d+)?', line)
                        if overall_throughput_match:
                            overall_throughput = float(overall_throughput_match.group())
                            operations_data[current_operation]['Overall throughput'].append(overall_throughput)
                    elif line.startswith('Performed'):
                        # Extract operation time using regular expression
                        operation_time_match = re.search(r'(\d+\.\d+) seconds', line)
                        if operation_time_match:
                            operation_time = float(operation_time_match.group(1))
                            operations_data[current_operation]['Operation time'].append(operation_time)

        return operations_data

    # Function to compute averages across all iterations for each operation
    def compute_averages_for_operations(log_filename_base, iterations):
        operations_data = defaultdict(lambda: {
            'PAPI instructions': [],
            'PAPI cycles': [],
            'IPC': [],
            'Overall throughput': [],
            'Operation time': []
        })

        for iteration in range(iterations):
            filename = f'{log_filename_base}_{iteration}.txt'
            iteration_data = parse_log_file(filename)

            for op, data in iteration_data.items():
                if data['PAPI instructions']:
                    operations_data[op]['PAPI instructions'].extend(data['PAPI instructions'])
                if data['PAPI cycles']:
                    operations_data[op]['PAPI cycles'].extend(data['PAPI cycles'])
                if data['IPC']:
                    operations_data[op]['IPC'].extend(data['IPC'])
                if data['Overall throughput']:
                    operations_data[op]['Overall throughput'].extend(data['Overall throughput'])
                if data['Operation time']:
                    operations_data[op]['Operation time'].extend(data['Operation time'])

        # Calculate averages for each operation type
        averaged_data = {}
        for op, data in operations_data.items():
            averaged_data[f'Avg PAPI instructions ({op})'] = (
                sum(data['PAPI instructions']) / len(data['PAPI instructions'])
                if data['PAPI instructions'] else None
            )
            averaged_data[f'Avg PAPI cycles ({op})'] = (
                sum(data['PAPI cycles']) / len(data['PAPI cycles'])
                if data['PAPI cycles'] else None
            )
            averaged_data[f'Avg IPC ({op})'] = (
                sum(data['IPC']) / len(data['IPC'])
                if data['IPC'] else None
            )
            averaged_data[f'Avg Overall throughput ({op})'] = (
                sum(data['Overall throughput']) / len(data['Overall throughput'])
                if data['Overall throughput'] else None
            )
            averaged_data[f'Avg Operation time ({op})'] = (
                sum(data['Operation time']) / len(data['Operation time'])
                if data['Operation time'] else None
            )

        return averaged_data

    # Function to write the result to a CSV file
    def write_to_csv(data, csv_filename):
        fieldnames = sorted(data.keys())
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(data)

    # Compute averages for operations
    averages_result = compute_averages_for_operations(log_filename_base, iterations)

    # Write result to CSV
    write_to_csv(averages_result, output_csv_filename)

    print(f"Averages for each benchmark operation have been written to '{output_csv_filename}'.")


parser = argparse.ArgumentParser(description='ECE361E HW2 - benchmark_run')  
parser.add_argument('--logname', type=str, default="exp1", help='base name for the log file')         
parser.add_argument('--benchmark', type=str, default="tp", help='which benchmark to run')
parser.add_argument('--devicenumber', type=str, default="mc1_08", help='which benchmark to run')
parser.add_argument('--iterations', type=int, default=3, help='number of iterations to run the benchmark') 
args = parser.parse_args()
logname_base = args.logname
benchmark = args.benchmark
device_number = args.devicenumber
iterations = args.iterations

# List to store results for all iterations
results = []
def rawdata_process():
    for i in range(iterations):
            file_name = f'{logname_base}_{i}_{benchmark.replace("/", "_")}.txt'
            output_file_name = f'{logname_base}_{i}_{benchmark.replace("/", "_")}.csv'

            # Convert the text file to a CSV file
            convert_txt_to_csv(file_name, output_file_name)

            time_find = f'{logname_base}_{i}_{benchmark.replace("/", "_")}_time.txt'
            with open(time_find, 'r') as file:
                content = file.read()

            # Use regular expressions to extract start and end times
            start_match = re.search(r'Start_time:\s*(\d+\.\d+)', content)
            end_match = re.search(r'End time:\s*(\d+\.\d+)', content)

            # Extract timestamps from the matches
            start_timestamp = float(start_match.group(1))
            end_timestamp = float(end_match.group(1))

            # Read the log file
            log = pd.read_csv(file_name, delim_whitespace=True)

            # Calculate start and end indices for benchmark data
            time = log['time'].to_numpy()
            bench_start = start_timestamp - time[0]
            bench_end = end_timestamp - time[0]
            start_idx = (time - time[0] < bench_start).nonzero()[0][-1]  # first time before bench start
            end_idx = (time - time[0] > bench_end).nonzero()[0][1]  # first time after bench end

            # Extract relevant columns
            w = log['power'].to_numpy()
            usage4 = log['usage_c4'].to_numpy()
            usage5 = log['usage_c5'].to_numpy()
            usage6 = log['usage_c6'].to_numpy()
            usage7 = log['usage_c7'].to_numpy()
            temp4 = log['temp4'].to_numpy()
            temp5 = log['temp5'].to_numpy()
            temp6 = log['temp6'].to_numpy()
            temp7 = log['temp7'].to_numpy()
            free_memory = log['free_memory'].to_numpy()
            used_memory = log['used_memory'].to_numpy()

            # Combine all temperature readings into one array and calculate average temperature
            all_temps = np.array([temp4, temp5, temp6, temp7])
            avg_temp = np.mean(all_temps)
            
            # Calculate power and energy when the benchmark is running
            w_active = w[start_idx:end_idx]
            energy = np.zeros(len(w_active))
            energy[0] = 0
            for j in range(1, len(energy)):
                energy[j] = energy[j - 1] + 0.2 * w_active[j - 1]

            # Calculate average little and big cluster voltages
            little_volts_active = log['little_micro_volts'].to_numpy()[start_idx:end_idx]
            big_volts_active = log['big_micro_volts'].to_numpy()[start_idx:end_idx]
            avg_little_volts = np.average(little_volts_active)
            avg_big_volts = np.average(big_volts_active)

            # Calculate runtime and average power
            runtime = bench_end - bench_start
            avg_p = np.average(w_active)

            # Calculate average and standard deviation for memory usage
            avg_free_memory = np.average(free_memory[start_idx:end_idx])
            avg_used_memory = np.average(used_memory[start_idx:end_idx])
            std_free_memory = np.std(free_memory[start_idx:end_idx])
            std_used_memory = np.std(used_memory[start_idx:end_idx])

            # Calculate standard deviation and standard deviation percentage for power and temperature
            std_p = np.std(w_active)
            std_p_percent = (std_p / avg_p) * 100 if avg_p != 0 else 0
            std_temp = np.std(all_temps)
            std_temp_percent = (std_temp / avg_temp) * 100 if avg_temp != 0 else 0

            # Calculate max, min, and median for energy and power
            max_energy = np.max(energy)
            min_energy = np.min(energy)
            median_energy = np.median(energy)
            max_power = np.max(w_active)
            min_power = np.min(w_active)
            median_power = np.median(w_active)

            # Append results to list
            results.append({
                'Iteration': i,
                'Runtime (s)': runtime,
                'Avg Power (W)': avg_p,
                'Avg Temp (C)': avg_temp,
                'Energy (J)': energy[-1],
                'Max Energy (J)': max_energy,
                'Min Energy (J)': min_energy,
                'Median Energy (J)': median_energy,
                'Avg Little Cluster Voltage (µV)': avg_little_volts,
                'Avg Big Cluster Voltage (µV)': avg_big_volts,
                'Std Power (W)': std_p,
                'Std Power (%)': std_p_percent,
                'Std Temp (C)': std_temp,
                'Std Temp (%)': std_temp_percent,
                'Max Power (W)': max_power,
                'Min Power (W)': min_power,
                'Median Power (W)': median_power,
                'Avg Free Memory (MB)': avg_free_memory,
                'Avg Used Memory (MB)': avg_used_memory,
                'Std Free Memory (MB)': std_free_memory,
                'Std Used Memory (MB)': std_used_memory
            })
def concatenate_averages_to_all_results(all_results_csv, averages_csv, output_csv):
    # Read the CSV files
    all_results_df = pd.read_csv(all_results_csv)
    averages_df = pd.read_csv(averages_csv)

    # Check if averages_df has exactly one row
    if len(averages_df) != 1:
        raise ValueError("averages_results.csv should contain exactly one row.")

    # Convert averages DataFrame to a single row DataFrame for concatenation
    averages_row = averages_df.iloc[0]

    # Replicate the averages_row DataFrame to match the number of rows in all_results_df
    averages_row_df = pd.DataFrame([averages_row] * len(all_results_df))

    # Concatenate the DataFrames horizontally
    combined_df = pd.concat([all_results_df, averages_row_df.reset_index(drop=True)], axis=1)

    # Write the combined DataFrame to a new CSV file
    combined_df.to_csv(output_csv, index=False)

    print(f"Combined results written to '{output_csv}'.")

def organize_files(logname_base, device_number, benchmark, iterations, measurement_results_csv, benchmark_results_csv, combined_results_csv):
    # Define the base directory
    base_dir = r'C:\Users\13462\Downloads\HW2'
    
    # Define the target directory
    target_dir = os.path.join(base_dir, f'{logname_base}_{device_number}_{benchmark}_{iterations}')
    
    # Create the directory if it does not exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    # Define the file names based on iterations
    for i in range(iterations):
        # Move each exp1_i_top.txt file
        source_file = f'{logname_base}_{i}_{benchmark.replace("/", "_")}.csv'
        if os.path.isfile(source_file):
            shutil.move(source_file, os.path.join(target_dir, source_file))
    
    # Define additional files to move
    for file in [measurement_results_csv, benchmark_results_csv, combined_results_csv]:
        if os.path.isfile(file):
            shutil.move(file, os.path.join(target_dir, file))

    results_file = 'results.txt'
    if os.path.isfile(results_file):
        shutil.move(results_file, os.path.join(target_dir, results_file))
    print(f"Files have been organized into '{target_dir}'.")

# Paths to the CSV files
output_csv = f'{logname_base}_{benchmark.replace("/", "_")}_combined_results.csv'

# Run the function

# Write all results to a CSV file
rawdata_process()
output_csv_file = f'{logname_base}_{benchmark.replace("/", "_")}_measurment_results.csv'
pd.DataFrame(results).to_csv(output_csv_file, index=False)

log_filename = 'results.txt'  # Replace with your actual log file name
output_csv_filename = 'benchmark_results.csv'
if(benchmark == 'tp'):
    process_benchmark_results_tp(log_filename, iterations, output_csv_filename)
elif benchmark == "bs":  # blackscholes
    print("Unknown benchmark specified.")        
elif benchmark == "bt":  # bodytrack
    print("Unknown benchmark specified.")
concatenate_averages_to_all_results(output_csv_file, output_csv_filename, output_csv)
organize_files(logname_base, device_number, benchmark, iterations, output_csv_file, output_csv_filename, output_csv)
print(f"\nAll results written")


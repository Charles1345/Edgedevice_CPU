import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import argparse
import warnings
import re
# Suppress FutureWarnings
warnings.filterwarnings("ignore", category=FutureWarning)

def read_data_from_directories(directories, log_name):
    all_data = []
    for directory in directories:
        file_path = os.path.join(directory, f"{log_name}_bt_measurment_results.csv")
        print(f"Trying to read file: {file_path}")  # Debug statement
        if os.path.isfile(file_path):
            try:
                data = pd.read_csv(file_path)
                print(f"Data from {file_path}: {data.head()}")  # Debug statement
                print(data.describe(include='all'))  # Additional data inspection
                data['Directory'] = directory  # Add directory column to identify the source
                all_data.append(data)
            except pd.errors.EmptyDataError:
                print(f"File is empty: {file_path}")
            except pd.errors.ParserError:
                print(f"Error parsing file: {file_path}")
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        else:
            print(f"File not found: {file_path}")
    
    if not all_data:
        raise ValueError("No data files found to concatenate.")
    return pd.concat(all_data, ignore_index=True)

def generate_box_plots(data, columns, plot_dir):
    # Calculate the number of rows and columns needed for subplots
    benchmark = benchmark.upper()
    num_columns = len(columns)
    num_rows = (num_columns + 1) // 2  # Two plots per row
    
    plt.figure(figsize=(15, 5 * num_rows))
    
    for i, column in enumerate(columns):
        plt.subplot(num_rows, 2, i + 1)
        try:
            # Check if column exists in data
            if column not in data.columns:
                print(f"Column {column} not found in data.")
                continue
            
            # Extract device information for x-axis labels
            data['Device'] = data['Directory'].apply(lambda x: re.search(r'mc1_(\d+)', x).group(1))
            data['Device'] = 'MC1-' + data['Device']
            
            # Create box plot
            sns.boxplot(x='Device', y=column, data=data)
            plt.title(f'Box Plot of {column} for {benchmark}')  # Adjusted metric unit
            plt.xlabel('Device')
            plt.ylabel(f'{column}')  # Adjusted metric unit
            plt.xticks(rotation=45)
            plt.grid(True)  # Add grid lines
            
        except KeyError:
            print(f"Column {column} not found in data.")
        except Exception as e:
            print(f"Error generating box plot for {column}: {e}")
    
    plt.tight_layout()
    
    # Ensure the plot directory exists
    os.makedirs(plot_dir, exist_ok=True)
    
    # Save the plot
    plot_path = os.path.join(plot_dir, 'individual_box_plots.png')
    plt.savefig(plot_path)
    plt.close()

def generate_scatter_plots(data, columns, plot_dir, logname, benchmark):
    benchmark = benchmark.upper()
    results_dir = os.path.join(plot_dir, f'scatter_plots_{logname}')
    os.makedirs(results_dir, exist_ok=True)

    # Create scatter plots for specified columns
    num_columns = len(columns)
    fig, axes = plt.subplots(nrows=num_columns, ncols=1, figsize=(12, 6 * num_columns))

    for i, column in enumerate(columns):
        try:
            if column not in data.columns:
                print(f"Column {column} not found in data.")
                continue

            sns.scatterplot(x='Device', y=column, data=data, ax=axes[i])
            axes[i].set_title(f'Scatter Plot of {column}')
            axes[i].set_xlabel('Device')
            axes[i].set_ylabel(f'{column}')
            axes[i].tick_params(axis='x', rotation=45)
            axes[i].grid(True)
        except KeyError:
            print(f"Column {column} not found in data.")
        except Exception as e:
            print(f"Error generating scatter plot for {column}: {e}")

    plt.tight_layout()
    plot_path = os.path.join(results_dir, 'combined_scatter_plots.png')
    plt.savefig(plot_path)
    plt.close()

def generate_combined_box_plots(data, columns, plot_dir, logname, benchmark):
    benchmark = benchmark.upper()
    results_dir = os.path.join(plot_dir, f'results_{logname}')
    os.makedirs(results_dir, exist_ok=True)
    
    data['Device'] = data['Directory'].apply(lambda x: re.search(r'mc1_(\d+)', x).group(1))
    data['Device'] = 'MC1-' + data['Device']

    # Calculate the difference between used mem and idle mem
    data['mem_diff [MB]'] = data['Avg Used Memory [MB]'] - data['Avg Free Memory [MB]']

    # Add the additional columns for memory metrics and their difference
    columns.extend(['mem_diff [MB]'])

    num_columns = len(columns)
    fig, axes = plt.subplots(nrows=num_columns, ncols=1, figsize=(12, 6 * num_columns))
    
    for i, column in enumerate(columns):
        try:
            if column not in data.columns:
                print(f"Column {column} not found in data.")
                continue

            sns.boxplot(x='Device', y=column, data=data, ax=axes[i])
            axes[i].set_title(f'Box Plot of {column}')
            axes[i].set_xlabel('Device')
            axes[i].set_ylabel(f'{column}')
            axes[i].tick_params(axis='x', rotation=45)
            axes[i].grid(True)
        except KeyError:
            print(f"Column {column} not found in data.")
        except Exception as e:
            print(f"Error generating box plot for {column}: {e}")

    plt.tight_layout()
    plot_path = os.path.join(results_dir, 'combined_box_plots.png')
    plt.savefig(plot_path)
    plt.close()

def generate_scatter_plots(data, columns, plot_dir, logname, category_name):
    results_dir = os.path.join(plot_dir, f'scatter_plots_{category_name}_{logname}')
    os.makedirs(results_dir, exist_ok=True)

    # Define color mapping for different metrics
    color_map = {
        'float ADD': 'blue',
        'float MAC.': 'green',
        'int ADD': 'red',
        'int MAC': 'purple'
    }

    # Create a figure with subplots
    num_columns = len(columns)
    if num_columns == 0:
        return
    
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(12, 8))

    for column in columns:
        try:
            if column not in data.columns:
                print(f"Column {column} not found in data.")
                continue

            # Extract type from the column name
            if 'float ADD' in column:
                color = color_map['float ADD']
            elif 'float MAC.' in column:
                color = color_map['float MAC.']
            elif 'int ADD' in column:
                color = color_map['int ADD']
            elif 'int MAC' in column:
                color = color_map['int MAC']
            else:
                color = 'black'  # Default color

            # Create scatter plot
            sns.scatterplot(x='Device', y=column, data=data, ax=axes, color=color, label=column)
            axes.set_title(f'Scatter Plot of {category_name}')
            axes.set_xlabel('Device')
            axes.set_ylabel(f'{category_name}')
            axes.tick_params(axis='x', rotation=45)
            axes.grid(True)
            axes.legend(title='Metric')
        except KeyError:
            print(f"Column {column} not found in data.")
        except Exception as e:
            print(f"Error generating scatter plot for {column}: {e}")

    plt.tight_layout()
    plot_path = os.path.join(results_dir, f'combined_scatter_plots_{category_name}.png')
    plt.savefig(plot_path)
    plt.close()

def generate_combinedscatter_power_plots(data, columns, plot_dir, logname, category_name):
    results_dir = os.path.join(plot_dir, f'scatter_plots_{category_name}_{logname}')
    os.makedirs(results_dir, exist_ok=True)

    # Extract the device number and use it as the grouping key
    data['Device'] = data['Directory'].apply(lambda x: re.search(r'mc1_(\d+)', x).group(1))
    data['Device'] = 'MC1-' + data['Device']

    # Select only numeric columns for aggregation
    numeric_data = data.select_dtypes(include='number')
    numeric_data['Device'] = data['Device']

    # Group by device and calculate the std and std percent for each metric across iterations
    grouped_data_mean = numeric_data.groupby('Device').mean().reset_index()
    grouped_data_std = numeric_data.groupby('Device').std().reset_index()

    for column in columns:
        if column not in grouped_data_mean.columns:
            print(f"Column {column} not found in data.")
            continue
        grouped_data_mean[f'{column}_std'] = grouped_data_std[column]
        grouped_data_mean[f'{column}_std_percent'] = (grouped_data_std[column] / grouped_data_mean[column]) * 100

    # Generate scatter plots for std
    fig, axes = plt.subplots(nrows=len(columns), ncols=1, figsize=(12, 6 * len(columns)))

    if len(columns) == 1:
        axes = [axes]  # Ensure axes is iterable when there's only one plot

    for i, column in enumerate(columns):
        try:
            if f'{column}_std' not in grouped_data_mean.columns:
                print(f"Column {column}_std not found in data.")
                continue

            sns.scatterplot(x='Device', y=f'{column}_std', data=grouped_data_mean, ax=axes[i])
            axes[i].set_title(f'Scatter Plot of {column} Std')
            axes[i].set_xlabel('Device')
            axes[i].set_ylabel(f'{column} Std')
            axes[i].tick_params(axis='x', rotation=45)
            axes[i].grid(True)
        except KeyError:
            print(f"Column {column}_std not found in data.")
        except Exception as e:
            print(f"Error generating scatter plot for {column}_std: {e}")

    plt.tight_layout()
    plot_path_std = os.path.join(results_dir, f'combined_scatter_plots_std_{category_name}.png')
    plt.savefig(plot_path_std)
    plt.close()

    # Generate scatter plots for std percent
    fig, axes = plt.subplots(nrows=len(columns), ncols=1, figsize=(12, 6 * len(columns)))

    if len(columns) == 1:
        axes = [axes]  # Ensure axes is iterable when there's only one plot

    for i, column in enumerate(columns):
        try:
            if f'{column}_std_percent' not in grouped_data_mean.columns:
                print(f"Column {column}_std_percent not found in data.")
                continue

            sns.scatterplot(x='Device', y=f'{column}_std_percent', data=grouped_data_mean, ax=axes[i])
            axes[i].set_title(f'Scatter Plot of {column} Std Percent')
            axes[i].set_xlabel('Device')
            axes[i].set_ylabel(f'{column} Std Percent')
            axes[i].tick_params(axis='x', rotation=45)
            axes[i].grid(True)
        except KeyError:
            print(f"Column {column}_std_percent not found in data.")
        except Exception as e:
            print(f"Error generating scatter plot for {column}_std_percent: {e}")

    plt.tight_layout()
    plot_path_std_percent = os.path.join(results_dir, f'combined_scatter_plots_std_percent_{category_name}.png')
    plt.savefig(plot_path_std_percent)
    plt.close()



def generate_scatter_power_plots(data, columns, plot_dir, logname, category_name):
    results_dir = os.path.join(plot_dir, f'scatter_plots_{category_name}_{logname}')
    os.makedirs(results_dir, exist_ok=True)

    num_columns = len(columns)
    if num_columns == 0:
        return
    
    fig, axes = plt.subplots(nrows=num_columns, ncols=1, figsize=(12, 6 * num_columns))

    if num_columns == 1:
        axes = [axes]  # Ensure axes is iterable when there's only one plot
    
    for i, column in enumerate(columns):
        try:
            if column not in data.columns:
                print(f"Column {column} not found in data.")
                continue

            sns.scatterplot(x='Device', y=column, data=data, ax=axes[i])
            axes[i].set_title(f'Scatter Plot of {column}')
            axes[i].set_xlabel('Device')
            axes[i].set_ylabel(f'{column}')
            axes[i].tick_params(axis='x', rotation=45)
            axes[i].grid(True)
        except KeyError:
            print(f"Column {column} not found in data.")
        except Exception as e:
            print(f"Error generating scatter plot for {column}: {e}")

    plt.tight_layout()
    plot_path = os.path.join(results_dir, f'scatter_plots_{category_name}.png')
    plt.savefig(plot_path)
    plt.close()


def separate_scatter_columns(scatter_columns):
    ipc_columns = [
        'Avg IPC (float ADD)',
        'Avg IPC (float MAC.)',
        'Avg IPC (int ADD)',
        'Avg IPC (int MAC)'
    ]

    operation_time_columns = [
        'Avg Operation time (float ADD)',
        'Avg Operation time (float MAC.)',
        'Avg Operation time (int ADD)',
        'Avg Operation time (int MAC)'
    ]

    overall_throughput_columns = [
        'Avg Overall throughput (float ADD)',
        'Avg Overall throughput (float MAC.)',
        'Avg Overall throughput (int ADD)',
        'Avg Overall throughput (int MAC)'
    ]

    papi_cycles_columns = [
        'Avg PAPI cycles (float ADD)',
        'Avg PAPI cycles (float MAC.)',
        'Avg PAPI cycles (int ADD)',
        'Avg PAPI cycles (int MAC)'
    ]

    return ipc_columns, operation_time_columns, overall_throughput_columns, papi_cycles_columns
def main():
    parser = argparse.ArgumentParser(description='Process benchmark data')
    parser.add_argument('--logname', type=str, default="exp1", help='Base name for the log files')
    parser.add_argument('--benchmark', type=str, default="tp", help='Benchmark name')
    parser.add_argument('--device_numbers', type=int, nargs='+', default=[8, 9], help='List of device numbers')
    parser.add_argument('--iterations', type=int, default=1, help='Fixed iteration number')
    args = parser.parse_args()

    logname_base = args.logname
    benchmark = args.benchmark
    device_numbers = args.device_numbers
    iteration = args.iterations

    # Specify the columns for box plots
    box_plot_columns = [
        'Runtime [s]',
        'Avg Power [W]',
        'Avg Temp [C]',
        'Energy [J]'
    ]
    power_columns = [
        'Std Power [W]',
        'Std Power [%]',
        'Std Temp [C]',
        'Std Temp [%]',
        'Std Energy [J]',
        'Std Energy [%]'
    ]

    combinedscatter_columns = [
        'Runtime [s]',
        'Avg Power [W]',
        'Avg Temp [C]',
        'Energy [J]'
    ]

    # Scatter plot columns
    # scatter_columns = [
    #     'Avg IPC (float ADD)',
    #     'Avg IPC (float MAC.)',
    #     'Avg IPC (int ADD)',
    #     'Avg IPC (int MAC)',
    #     'Avg Operation time (float ADD)',
    #     'Avg Operation time (float MAC.)',
    #     'Avg Operation time (int ADD)',
    #     'Avg Operation time (int MAC)',
    #     'Avg Overall throughput (float ADD)',
    #     'Avg Overall throughput (float MAC.)',
    #     'Avg Overall throughput (int ADD)',
    #     'Avg Overall throughput (int MAC)',
    #     'Avg PAPI cycles (float ADD)',
    #     'Avg PAPI cycles (float MAC.)',
    #     'Avg PAPI cycles (int ADD)',
    #     'Avg PAPI cycles (int MAC)'
    # ]

    # Separate the scatter plot columns into categories
    # ipc_columns, operation_time_columns, throughput_columns, papi_cycles_columns = separate_scatter_columns(scatter_columns)
    

    all_data = pd.DataFrame()

    for device_number in device_numbers:
        directory = f'{logname_base}_mc1_{device_number}_{benchmark}_{iteration}'
        try:
            data = read_data_from_directories([directory], logname_base)
            all_data = pd.concat([all_data, data], ignore_index=True)
            # generate_box_plots(data, box_plot_columns, directory)
        except ValueError as e:
            print(e)  # Handle the case where no data is available

    if not all_data.empty:
        generate_combined_box_plots(all_data, box_plot_columns, 'plots1', logname_base, benchmark)
        generate_scatter_power_plots(all_data, power_columns, 'plots2', logname_base, benchmark)
        generate_combinedscatter_power_plots(all_data, combinedscatter_columns, 'plots3', logname_base, benchmark)
        # generate_scatter_plots(all_data, ipc_columns, 'plots', logname_base, 'ipc')
        # generate_scatter_plots(all_data, operation_time_columns, 'plots', logname_base, 'operation_time')
        # generate_scatter_plots(all_data, throughput_columns, 'plots', logname_base, 'throughput')
        # generate_scatter_plots(all_data, papi_cycles_columns, 'plots', logname_base, 'papi_cycles')

if __name__ == "__main__":
    main()

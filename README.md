EdgeDevice_CPU

Research Project: CPU Performance Benchmarking on Edge Devices

This project measures and analyzes the CPU performance of remote edge devices using automated benchmarking scripts and post-processing tools.

Overview

You will:

Transfer the benchmarking scripts to the remote edge device.

Run a controlled benchmark on the device.

Retrieve the experiment data to your local machine.

Save and process the results for analysis.

This workflow ensures consistent and repeatable CPU performance evaluations across multiple devices.

Prerequisites

SSH access to the edge device (e.g., student@sld-mc1-08.ece.utexas.edu
)

Python 3.x installed on both your laptop and the edge device

Sudo privileges on the edge device

Benchmark scripts: run_benchmark.py and DataProcessing.py

Stable network connectivity between your laptop and the device

Step-by-Step Instructions
1. Copy the benchmark scripts to the edge device

Use the following command to copy your project folder from your local machine to the edge device:

scp -r /path/to/your/project student@sld-mc1-08.ece.utexas.edu:/home/student


This uploads your files to the device’s home directory (/home/student).

2. Run the benchmark on the edge device

SSH into the device and execute:

sudo python run_benchmark.py --logname exp1 --iterations 3 --benchmark tp --port 9070


Parameter meanings:
--logname exp1 : name of the experiment log (example: exp1)
--iterations 3 : number of times to repeat the test for accuracy
--benchmark tp : benchmark type (example: throughput test)
--port 9070 : network port used for measurement

This runs the CPU performance test and saves the raw results in the HW2 directory on the device.

3. Transfer the results back to your laptop

After the benchmark finishes, copy the generated data files back to your local system:

scp -r student@sld-mc1-08.ece.utexas.edu:/home/student/HW2 /path/to/your/local/folder


This downloads all logs and raw measurement data for further analysis.

4. Save the benchmark output to a results file

Inside your local copy of the experiment directory (/path/to/your/local/folder/HW2), create a new file called results.txt.
Copy and paste the printed output from the benchmark (shown on screen during step 2) into results.txt.
This provides a readable summary of the experiment’s terminal output.

5. Process the data locally

Run the provided post-processing script on your laptop to analyze and visualize the results:

python DataProcessing.py --logname exp1 --iterations 3 --benchmark tp --devicenumber mc1_08


Parameter meanings:
--logname exp1 : must match the name used during benchmarking
--iterations 3 : same number of iterations as before
--benchmark tp : benchmark type
--devicenumber mc1_08 : identifier for the tested edge device

This script parses results.txt and generates statistical summaries, graphs, and structured data files inside a new results directory.

6. Verify results and clean up

After successful processing:

A new folder (for example, HW2/results_exp1_mc1_08) will be created containing processed data and figures.

Once verified, delete the redundant HW2 folder copied from the device to save storage space.

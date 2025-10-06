# EdgeDevice_CPU
Research Project: CPU Performance Benchmarking on Edge Devices

This project measures and analyzes the CPU performance of remote edge devices using automated benchmarking scripts and post-processing tools.

---

## Overview
You will:
1. Transfer the benchmarking scripts to the remote edge device.
2. Run a controlled benchmark on the device.
3. Retrieve the experiment data to your local machine.
4. Save and process the results for analysis.

This workflow ensures consistent and repeatable CPU performance evaluations across multiple devices.

---

## Prerequisites
- SSH access to the edge device (e.g., `student@sld-mc1-08.ece.utexas.edu`)
- Python 3.x installed on both your laptop and the edge device
- Sudo privileges on the edge device
- Benchmark scripts: `run_benchmark.py` and `DataProcessing.py`
- Stable network connectivity between your laptop and the device

---

## Step-by-Step Instructions

### 1. Copy the benchmark scripts to the edge device
Use the following command to copy your project folder from your local machine to the edge device:
```bash
scp -r /path/to/your/project student@sld-mc1-08.ece.utexas.edu:/home/student

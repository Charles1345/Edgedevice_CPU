import sysfs_paths as sysfs
import subprocess
import sys
import argparse
import time
import argparse
import subprocess
import threading 
import socket 
import psutil
import telnetlib as tel
import numpy as np
import logging


#command line: 
#sudo python run_benchmark.py --logname exp1 --iterations 3 --benchmark tp --host sld-mc1-04.ece.utexas.edu --port 9020

def get_avail_freqs(cluster):
    """
    Obtain the available frequency for a cpu. Return unit in khz by default!
    """
    # Read cpu freq from sysfs_paths.py
    freqs = open(sysfs.fn_cluster_freq_range.format(cluster)).read().strip().split(' ')
    return [int(f.strip()) for f in freqs]

def get_cluster_freq(cluster_num):
    """
    Read the current cluster freq. cluster_num must be 0 (little) or 4 (big)
    """
    with open(sysfs.fn_cluster_freq_read.format(cluster_num), 'r') as f:
        return int(f.read().strip())

def set_user_space(clusters=None):
    """
    Set the system governor as 'userspace'. This is necessary before you can change the
    cluster/cpu freq to customized values
    """
    print("Setting userspace")
    clusters = [0, 4]
    for i in clusters:
        with open(sysfs.fn_cluster_gov.format(i), 'w') as f:
            f.write('userspace')


def set_cluster_freq(cluster_num, frequency):
    """
    Set customized freq for a cluster. Accepts frequency in khz as int or string
    """
    with open(sysfs.fn_cluster_freq_set.format(cluster_num), 'w') as f:
        f.write(str(frequency))

def get_telnet_power(telnet_connection, last_power):
    """
    Read power values using telnet.
    """
    # Get the latest data available from the telnet connection without blocking
    tel_dat = str(telnet_connection.read_very_eager())
    # Find the latest power measurement in the data
    idx = tel_dat.rfind('\n')
    idx2 = tel_dat[:idx].rfind('\n')
    idx2 = idx2 if idx2 != -1 else 0
    ln = tel_dat[idx2:idx].strip().split(',')
    if len(ln) < 2:
        total_power = last_power
    else:
        total_power = float(ln[-2])
    return total_power

def get_cpu_load():
    """
    Returns the CPU load as a value from the interval [0.0, 1.0]
    """
    loads = [x / 100 for x in psutil.cpu_percent(interval=None, percpu=True)]
    return loads

def get_temps():
    """
    Obtain the temp values from sysfs_paths.py
    """
    templ = []
    # Get temp from temp zones 0-3 (the big cores)
    for i in range(4):
        temp = float(open(sysfs.fn_thermal_sensor.format(i), 'r').readline().strip()) / 1000
        templ.append(temp)
    # Note: on the Exynos5422, CPU temperatures 5 and 7 (big cores 1 and 3, counting from 0) appear to be swapped.
    # Therefore, swap them back.
    t1 = templ[1]
    templ[1] = templ[3]
    templ[3] = t1
    return templ

def get_micro_volts(voltage_path):
    with open(voltage_path, 'r') as f:
        return int(f.read().strip())

def get_core_freq(core_num):
    with open(sysfs.fn_cpu_freq_read.format(core_num), 'r') as f:
        return int(f.read().strip())


def get_little_micro_volts():
    little_cluster_voltage_base = "/sys/devices/platform/pwrseq/subsystem/devices/s2mps11-regulator/regulator/regulator.44/"
    little_micro_volts = little_cluster_voltage_base + "microvolts"
    return get_micro_volts(little_micro_volts)

def get_big_micro_volts():
    big_cluster_voltage_base = "/sys/devices/platform/pwrseq/subsystem/devices/s2mps11-regulator/regulator/regulator.40/"
    big_micro_volts = big_cluster_voltage_base + "microvolts"
    return get_micro_volts(big_micro_volts)


def get_memory_usage():
    output = subprocess.check_output(['free', '-m']).decode('utf-8')
    lines = output.splitlines()
    if len(lines) >= 2:
        # Extract and return used and free memory values
        fields = lines[1].split()
        if len(fields) >= 7:
            used_memory = int(fields[2])
            free_memory = int(fields[3])
            return used_memory, free_memory
    return None, None

measurement_started_event = threading.Event()

def run_measurement(out_fname, stop_event):
    header = "time\tpower\tusage_c0\tusage_c1\tusage_c2\tusage_c3\tusage_c4\tusage_c5\tusage_c6\tusage_c7\ttemp4\ttemp5\ttemp6\ttemp7\tlittle_micro_volts\tbig_micro_volts\tused_memory\tfree_memory\tlittle_core_freq\tbig_core_freq"
    out_file = open(out_fname, 'w')
    out_file.write(header)
    out_file.write("\n")

    telnet_connection = tel.Telnet("192.168.4.1")
    total_power = 0.0
    measurement_started_event.set() 
    while not stop_event.is_set():
        last_time = time.time()

        # System power
        total_power = get_telnet_power(telnet_connection, total_power)
    
        # CPU load
        usages = get_cpu_load()

        # Temperature for big cores
        temps = get_temps()

        # Big cluster core frequency
        big_core_freqs = 2000000
      
        # Little cluster core frequency
        little_core_freqs = 200000
    
        # Micro volts for little and big clusters
        little_mv = get_little_micro_volts()
        big_mv = get_big_micro_volts()

        # Memory usage
        used_memory, free_memory = get_memory_usage()
    
        # Timestamp
        time_stamp = last_time

        # Data write out:
        fmt_str = "{}\t" * 20  # Adjusted for 27 fields now
        out_ln = fmt_str.format(time_stamp, total_power, usages[0], usages[1], usages[2], usages[3], usages[4], usages[5],
                                usages[6], usages[7], temps[0], temps[1], temps[2], temps[3], little_mv, big_mv,
                                used_memory, free_memory, little_core_freqs, big_core_freqs)

        out_file.write(out_ln)
        out_file.write("\n")

        # Sleep to maintain sampling rate
        elapsed = time.time() - last_time
        DELAY = 0.2  # sample every 200 ms
        time.sleep(max(0., DELAY - elapsed))


#run_benchmark 
parser = argparse.ArgumentParser(description='ECE361E HW2 - benchmark_run')  
parser.add_argument('--logname', type=str, default="exp1", help='base name for the log file')         
parser.add_argument('--benchmark', type=str, default="tp", help='which benchmark to run')
parser.add_argument('--iterations', type=int, default=3, help='number of iterations to run the benchmark')
parser.add_argument('--host', default="127.0.0.1", help='IP address of the device')
parser.add_argument('--port', type=int, default=10001, help='Port for the device to listen on')
args = parser.parse_args()
logname_base = args.logname
benchmark = args.benchmark
iterations = args.iterations
host = args.host
port = args.port



for i in range(iterations):
        print('Available freqs for big cluster:', get_avail_freqs(4))
        print('Available freqs for LITTLE cluster:', get_avail_freqs(0))
        set_user_space()

        set_cluster_freq(4, 2000000)   # big cluster --> 2 GHz
        set_cluster_freq(0, 200000)    # little cluster --> 0.2 GHz

        # print current freq for the little cluster and big cluster
        print('Current freq for big cluster:', get_cluster_freq(4))
        print('Current freq for little cluster:', get_cluster_freq(0))
        out_fname = f'{logname_base}_{i}_{benchmark.replace("/", "_")}.txt'
        print(f"Starting iteration {i} of {iterations}, logging to {out_fname}")


        # Create a socket object
        soc = socket.socket()
        # Set the socket to reuse the address
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind the socket to the host and port
        soc.bind((host, port))

        stop_event = threading.Event()
        t1 = threading.Thread(target=run_measurement, args=(out_fname, stop_event))
        t1.start()
        print("Measurement thread started.")
        
        measurement_started_event.wait()
        time.sleep(2)  # Adjust delay as needed
        # run the benchmark
        start = time.time()
        if benchmark == "tp":  # TPBench
            command = "taskset --all-tasks 0x10 /home/student/HW2_files/TPBench.exe"  # 0x10: core 4 (7 6 5 4 3 2 1 0)
        
        elif benchmark == "bs":  # blackscholes
            command = "taskset --all-tasks 0xF0 /home/student/HW2_files/parsec_files/blackscholes 4 /home/student/HW2_files/parsec_files/in_10M_blackscholes.txt out"  # 0xF0: cores 7654, 4 threads
           
        elif benchmark == "bt":  # bodytrack
            command = "taskset --all-tasks 0xF0 /home/student/HW2_files/parsec_files/bodytrack /home/student/HW2_files/parsec_files/sequenceB_261 4 260 3000 8 3 4 0"  # 0xF0: core 7654, 4 threads
      
        else:
            print("Unknown benchmark specified.")
            sys.exit(1)

        proc_ben = subprocess.Popen(command.split())  # Use Popen to start the subprocess asynchronously
    # Wait for the benchmark process to finish and measure its runtime
        proc_ben.wait()
        # measure the time to run the benchmark

        total_time = time.time() - start
        print(f"Iteration {i + 1} benchmark runtime: {total_time} seconds")
        print("Start time: ", start, " End time: ", start + total_time)

        # Log the start and end times to a file
        time_find = f'{logname_base}_{i}_{benchmark.replace("/", "_")}_time.txt'
        with open(time_find , 'w') as log_file:
            log_file.write(f"Start_time: {start}\n")
            log_file.write(f"End time: {start+total_time}\n")

        time.sleep(2)
        # Stop the power and temperature recording thread if it's running
        if stop_event:
            stop_event.set()
            t1.join()
            measurement_started_event.clear()
        # Close the socket
        soc.close()
        print("-" * 50)
        print(f"Waiting 2 minutes for devices to cool down...")
        time.sleep(120) # Wait for 2 minutes for devices to cool down
        print(f"Data Processing done")

print("All iterations completed.")



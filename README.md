# Edgedevice_CPU
Reserach on CPU performance of edge devices 
Instructions on Running the code: 
1. Copy the file to the edge devices using this command: scp -r (your_file_path) student@sld-mc1-08.ece.utexas.edu:/home/student
2. Run the following command to start measurement and benchmark: sudo python run_benchmark.py --logname exp1 --iterations 3 --benchmark tp --port 9070
3. After the execution of the benchmark, first transfer all the files back to the laptop using this command: scp -r student@sld-mc1-08.ece.utexas.edu:/home/student/HW2  your file path 
4. Now inside the your_file_path_HW2/HW2 file, create a results.txt file, copy and paste the output results from running the benchmark to results.txt
5. After results.txt is created and loaded, run the following command: python python DataProcessing.py --logname exp1 --iterations 3 --benchmark tp --devicenumber mc1_08
6. Lastly, the directory that has all the results will be created for this experiment in the HW2 file, and then delete the HW2/HW2 file that is copied from the device

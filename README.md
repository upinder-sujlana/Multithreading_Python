# Multithreading Demo in Python

Python script utlizing multthreading capability. In the example I create 4 threads (number can be changed) which shall envoke run_remote_cmd worker function.

In the script I am using two Queues. One queue (work_queue) holds all commands that need to be run remotely on a linux machine. The second Queue is results_queue which shall hold the results generated by the work done by the threads.

Each thread instance goes and gets one command out of the work_queue and then runs it and puts the results in the resulsts_queue. 

Eventually I take the results out of the results_queue and convert it into a dictionary to then be printed out.

The script also needs paramiko library installed.

The script at the moment a hardcoded IP of the remote linux box. Change to the IP of your choice.

Additionally the script picks picks USERNAME and PASSWORD enviromental variable. Please set them accordingly.

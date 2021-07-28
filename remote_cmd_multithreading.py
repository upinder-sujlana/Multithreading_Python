#! /usr/bin/python3

import logging
import os
import sys
from queue import Queue, Empty
from threading import Thread

try:
    import paramiko
except ImportError:
    raise ImportError("Could not import paramiko. Please install it.")
    sys.exit(1)
#-----------------------------------------------------------------------------
__author__     = 'Upinder Sujlana'
__copyright__  = 'Copyright 2021'
__version__    = '1.0.0'
__maintainer__ = 'Upinder Sujlana'
__status__     = 'demo'
#-----------------------------------------------------------------------------
DEBUG=False
TIME_OUT = 30
THREAD_POOL_SIZE = 4

#----------------------------------------------------------------------------------------------------------
logfilename=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'threading.log')
logging.basicConfig(
    level=logging.ERROR,
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%d-%m-%Y:%H:%M:%S',
    handlers=[
        logging.FileHandler(logfilename, mode='a'),
        logging.StreamHandler()
    ]
)
#----------------------------------------------------------------------------------------------------------
def run_remote_cmd(ip, username, password, timeout, cmd):
    try:
        if DEBUG:
            logging.debug('Starting the run_remote_cmd()')
        client = paramiko.SSHClient()
        # Automatically add untrusted hosts (Handle SSH Exception for unknown host)
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=ip, username=username, password=password, timeout=TIME_OUT)
        if DEBUG:
            logging.debug('Ending the run_remote_cmd()')
    except paramiko.AuthenticationException as error:
        print ("Error in Authenticating")
        logging.error("AuthenticationException has occured, stacktrace : ", exc_info=True)
        logging.shutdown()
        sys.exit(1)

    except:
        print ("Exception")
        logging.error("An exception has occured, stacktrace : ", exc_info=True)
        logging.shutdown()
        sys.exit(1)    

    (stdin, stdout, stderr) = client.exec_command(cmd)

    buff=[]
    for line in stdout.readlines():
        buff.append(line)        

    #Closing the paramiko connection
    client.close()

    return buff
#----------------------------------------------------------------------------------------------------------
def worker(work_queue, results_queue):
    while not work_queue.empty():
        try:
            command = work_queue.get_nowait()
        except Empty:
            break
        try:
            #Picking the Username and password from enviromental variable use the format: export USERNAME='sjs'
            try:
                user_name=os.environ.get('USERNAME')
                pass_word=os.environ.get('PASSWORD')
            except:
                logging.error("Could not get the username and password from enviromental variable. Exiting.", exc_info=True)
                sys.exit(1)
            
            #Now lets get the thread worker to invoke the run_remote_cmd worker function.
            result = run_remote_cmd(ip='10.201.254.110', username=user_name, password=pass_word, timeout=30, cmd=command)
        except Exception as err:
            results_queue.put( (command,err) )
        else:
            results_queue.put( (command, result) )
        finally:
            work_queue.task_done()

#----------------------------------------------------------------------------------------------------------
def present_result(result):
    for k in result:
        print ("Command Ran :- " + k)
        print ("Output :- \n")
        for x in result[k]:
            print (x)
        print ("\n==================================================================================\n")
#----------------------------------------------------------------------------------------------------------
def main():
    work_queue = Queue()
    results_queue = Queue()

    commands = [
    "ifconfig | grep -E 'inet addr|HW' | grep -v '127.0.0.1'",
    "id",
    "uname -a",
    "df -h"]

    #Populate the commands we want to be run
    for command in commands:
        work_queue.put(command)
    #Create a factory of threads
    threads=[]
    for _ in range(THREAD_POOL_SIZE):
        threads.append( Thread(target=worker, args=(work_queue, results_queue)) )
    #start the threads
    for thread in threads:
        thread.start()
    #Use the work_queue to block till commands processed
    work_queue.join()
    #Print out the results_queue
    results_dict={}   
    while not results_queue.empty():
        cmd_key, output_value = results_queue.get()
        #print (cmd_key)
        #print (output_value)
        #print (result)
        if isinstance(output_value, Exception):
            raise cmd_key
        #No error so lets print out the result
        results_dict[cmd_key]=output_value
    present_result(results_dict)


#----------------------------------------------------------------------------------------------------------
if __name__ ==  '__main__':
    main()
#!.venv/bin/python3
'''
    launcher.py
    Manage the lifecycle of the Pi-Star CallerID application
    Description: This is the main file that will be used to launch the application. Note: can be run directly from the command line without calling python
    if the file has the correct permissions.
    Author: Jonathan L. Pressler
    Date: 2024/04/07
    Version: 1.1
'''

import subprocess
import argparse
import os

if __name__ == '__main__':
    '''
    This block of code is used to run the Pi-Star CallerID application.
    
    This script is used to manage the lifecycle of the Pi-Star CallerID application. It can start, stop, update, and eventually check the status of the application.
    
    The following command is used to start the API and Web applications:
    nohup python api.py > api.log 2>&1 &
    nohup python -m web.web > web.log 2>&1 &
    
    The following command is used to kill the processes:
    kill -9 <PID>
    
    The following command is used to update the application:
    git pull
    
    The following command is used to check for updates:
    git fetch
    
    The following command is used to check for changes:
    git diff HEAD origin/main
    
    This script supports the following command line arguments:
    -k, --kill: Kill the running processes
    -u, --update: Update the application
    
    If the script is run without any arguments, it will start the processes.
    
    Example:
    ./launcher.py -k -- Kill the running processes
    ./launcher.py -u -- Update the application
    ./launcher.py -- Start the processes (The script will check for updates every time it is run)
    
    Exceptions:
        FileNotFoundError: An exception that is raised when the PIDs file is not found
        PermissionError: An exception that is raised when there is a permission error
        subprocess.CalledProcessError: An exception that is raised when there is an error running the commands
        Exception: An exception that is raised when an unknown error occurs
        
    TODO:
        - Add support for checking the status of the processes
        - Add support for restarting the processes
    '''
    current_dir = os.path.dirname(os.path.realpath(__file__))
    is_service = False
    pid_path = 'pids.txt'
    if current_dir == '/usr/local/lib/callerid':
        # If the script is run from the /usr/local/lib/callerid directory, the log files will be written to /var/lib/callerid
        # This is because when running from Pi-Star, the /usr/local/lib/callerid directory is read-only.
        # We also set the is_service variable to True for further code to be aware that the script is running as a service.
        is_service = True
        pid_path = '/var/lib/callerid/pids.txt'
        api_command = 'nohup .venv/bin/python3 -m api.api > /var/lib/callerid/api.log 2>&1 &'
        web_command = 'nohup .venv/bin/python3 -m web.web > /var/lib/callerid/web.log 2>&1 &'
    else:
        api_command = 'nohup .venv/bin/python3 -m api.api > api.log 2>&1 &'
        web_command = 'nohup .venv/bin/python3 -m web.web > web.log 2>&1 &'
    arg_parser = argparse.ArgumentParser(description='Launch the Pi-Star CallerID application')
    arg_parser.add_argument('-k', '--kill', action='store_true', help='Kill the running processes')
    arg_parser.add_argument('-u', '--update', action='store_true', help='Update the application')
    args = arg_parser.parse_args()
    if args.kill:
        try:
            with open(pid_path, 'r') as f:
                api_pid = f.readline().strip().split()[-1]
                web_pid = f.readline().strip().split()[-1]
        except FileNotFoundError:
            print('No PIDs found. Are you sure the processes are running?')
            exit(1)
        except Exception as e:
            print(f'Error: {e}')
            print('An unknown error occurred. Please check the error message and try again.')
            exit(1)
        try:
            subprocess.run(['kill', '-9', api_pid]) # Force kill the process (if the API is being accessed, it will not close until the connection is closed or the process is killed forcefully)
            subprocess.run(['kill', web_pid])
            print(f'Killed the processes with PIDs: {api_pid} and {web_pid}')
            os.remove(pid_path)
            exit(0)
        except PermissionError as e:
            print(f'Error: {e}')
            print('Did you start the processes with sudo or as root?/n Or is the filesystem in Read-Only mode?')
            print('Please check the permissions and try again.')
            exit(1)
        except subprocess.CalledProcessError as e:
            print(f'Error: {e}')
            print('There was an error running the commands. Please check the commands and try again.')
            exit(1)
        except Exception as e:
            print(f'Error: {e}')
            print('An unknown error occurred. Please check the error message and try again.')
            exit(1)
    elif args.update:
        try:
            result = subprocess.check_output(['git', 'pull'], text=True)
            if 'Already up to date' in result:
                print('No changes were made to the repository.')
                exit(0)
            elif 'stash' in result:
                print('Changes were made to the repository. Please stash or commit the changes and try again.')
                exit(1)
            print('Updated the application.\nIf changes other than to web related files were made, please restart the application.')
            exit(0)
        except subprocess.CalledProcessError as e:
            print(f'Error: {e}')
            print('There was an error pulling the repository. Please check the git error message and try again.')
            exit(1)
        except Exception as e:
            print(f'Error: {e}')
            print('An unknown error occurred. Please check the error message and try again.')
            exit(1)
    
    try:
        if os.path.exists(pid_path):
            with open(pid_path, 'r') as f:
                print('PIDs file found. Checking if the processes are running...')
                api_pid = f.readline().strip().split()[-1]
                web_pid = f.readline().strip().split()[-1]
            if subprocess.run(['ps', '-p', api_pid], stdout=subprocess.PIPE).returncode == 0:
                print(f'API process with PID {api_pid} is running.')
            else:
                print(f'API process with PID {api_pid} is not running.')
                api_pid = None
            if subprocess.run(['ps', '-p', web_pid], stdout=subprocess.PIPE).returncode == 0:
                print(f'Web process with PID {web_pid} is running.')
            else:
                print(f'Web process with PID {web_pid} is not running.')
                web_pid = None
            if api_pid is not None and web_pid is not None:
                print('Both processes are running. If you want to kill the processes, run the script with the -k or --kill option.')
                exit(1)
            elif api_pid is not None:
                print('API process is running. If you want to kill the process, run the script with the -k or --kill option.')
                exit(1)
            elif web_pid is not None:
                print('Web process is running. If you want to kill the process, run the script with the -k or --kill option.')
                exit(1)
            else:
                print('No processes are running. Starting the processes...')
        try:
            subprocess.check_output(['git', 'fetch'], text=True)
            update_available = subprocess.check_output(['git', 'diff', 'HEAD', 'origin/main'], text=True)
            if update_available:
                print('Update available. Please run the script with the -u or --update option to update the application.')
        except subprocess.CalledProcessError as e:
            print(f'Error checking for updates: {e}')
        subprocess.run(api_command, shell=True)
        subprocess.run(web_command, shell=True)
        api_pid = subprocess.check_output(['pgrep', '-f', 'api.api'], text=True).strip().split()[-1]
        web_pid = subprocess.check_output(['pgrep', '-f', 'web.web'], text=True).strip().split()[-1]
        with open(pid_path, 'w') as f:
            f.write(f'API PID: {api_pid}\n')
            f.write(f'Web PID: {web_pid}\n')
        print(f'API PID: {api_pid}')
        print(f'Web PID: {web_pid}')
    except PermissionError as e:
        print(f'Error: {e}')
        print('Most likely the filesystem is in Read-Only mode. Please check the filesystem and try again.')
    except OSError as e:
        print(f'Error: {e}')
        print('There was an error running the commands. Please check the commands and try again.')
    except subprocess.CalledProcessError as e:
        print(f'Error: {e}')
        print('There was an error running the commands. Please check the commands and try again.')
    except Exception as e:
        print(f'Error: {e}')
        print('An unknown error occurred. Please check the error message and try again.')
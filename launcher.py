#/home/jonathan/Parrot/.venv/bin/python
# Description: This is the main file that will be used to launch the application
import subprocess
import argparse
import os

if __name__ == '__main__':
    api_command = 'nohup python api.py > api.log 2>&1 &'
    web_command = 'nohup python -m web.web > web.log 2>&1 &'
    arg_parser = argparse.ArgumentParser(description='Launch the Parrot application')
    arg_parser.add_argument('-k', '--kill', action='store_true', help='Kill the running processes')
    arg_parser.add_argument('-u', '--update', action='store_true', help='Update the application')
    args = arg_parser.parse_args()
    if args.kill:
        try:
            with open('pids.txt', 'r') as f:
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
            os.remove('pids.txt')
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
        if os.path.exists('pids.txt'):
            with open('pids.txt', 'r') as f:
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
        api_pid = subprocess.check_output(['pgrep', '-f', 'api.py'], text=True).strip().split()[-1]
        web_pid = subprocess.check_output(['pgrep', '-f', 'web.web'], text=True).strip().split()[-1]
        with open('pids.txt', 'w') as f:
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
    except KeyboardInterrupt:
        print('Exiting...')
        with open('pids.txt', 'r') as f:
            api_pid = f.readline().strip().split()[-1]
            web_pid = f.readline().strip().split()[-1]
        subprocess.run(['kill', api_pid])
        subprocess.run(['kill', web_pid])
        print(f'Killed the processes with PIDs: {api_pid} and {web_pid}')
        exit(0)
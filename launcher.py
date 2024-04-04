# Description: This is the main file that will be used to launch the application
import subprocess

if __name__ == '__main__':
    api_command = 'nohup python api.py > api.log 2>&1 &'
    web_command = 'nohup python -m web.web > web.log 2>&1 &'
    subprocess.run(api_command, shell=True)
    subprocess.run(web_command, shell=True)
    api_pid = subprocess.check_output(['pgrep', '-f', 'api.py'], text=True).strip().split()[-1]
    web_pid = subprocess.check_output(['pgrep', '-f', 'web.web'], text=True).strip().split()[-1]
    with open('pids.txt', 'w') as f:
        f.write(f'API PID: {api_pid}\n')
        f.write(f'Web PID: {web_pid}\n')
    print(f'API PID: {api_pid}')
    print(f'Web PID: {web_pid}')
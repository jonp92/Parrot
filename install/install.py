import venv
import subprocess
import os
import json

'''
Installer is a class that installs the Pi-Star CallerID application.

The installer class is used to install the Pi-Star CallerID application. It creates a virtual environment, installs the requirements,
copies the files to the install directory, and sets up the systemd service.

Variables:
    script_dir: A string that represents the directory of the script

Methods:
    create_venv(venv_dir: str = '.venv', install_requirements: bool = True): Creates a virtual environment for the Pi-Star CallerID application.
    install(install_dir: str = '/usr/local/lib/callerid'): Installs the Pi-Star CallerID application.

Returns:
    None
    
Exceptions:
    FileExistsError: An exception that is raised when the virtual environment already exists
    PermissionError: An exception that is raised when there is a permission error
    Exception: An exception that is raised when an unknown error occurs

TODO:
    - Add support for uninstalling the application
    - Add support for updating the application
'''

class Installer:
    def __init__(self):
        if os.geteuid() != 0:
            print('Please run the script with elevated privileges.')
            exit(1)
        self.script_dir = os.path.dirname(os.path.realpath(__file__)) # Get the directory of the script, not the (CWD)
        self.tmpfs_dir = '/var/lib/callerid'
        config_path = os.path.join(self.script_dir, '..', 'config.json')
        self.config = json.load(open(config_path)) if os.path.isfile(config_path) else None
        if self.config:
            for key in self.config:
                setattr(self, key, self.config[key])
                if self.config[key] == "True":
                    setattr(self, key, True)
                elif self.config[key] == "False":
                    setattr(self, key, False)
        else:
            print('config.json not found. Please create a config.json file in the root directory. Exiting...')
            exit(1)

    def create_venv(self, venv_parent_dir: str, install_requirements: bool = True):
        '''
        create_venv is a function that creates a virtual environment for the Pi-Star CallerID application.
        
        Parameters:
            install_requirements: A boolean that represents whether the requirements should be installed
            If True, the requirements will be installed if not already installed, otherwise, the requirements will not be installed automatically
            
        Variables:
            venv_dir: A string that represents the directory where the virtual environment will be created
            venv: A venv.EnvBuilder object that is used to create the virtual environment
        
        Returns:
            None
        
        Exceptions:
            FileExistsError: An exception that is raised when the virtual environment already exists
            PermissionError: An exception that is raised when there is a permission error
            Exception: An exception that is raised when an unknown error occurs
        '''
        venv_dir = '.venv'
        full_dir = f'{venv_parent_dir}/{venv_dir}'
        
        try:
            venv.EnvBuilder(with_pip=True).create(full_dir)
            print('Virtual environment created successfully.')
        except FileExistsError:
            print('Virtual environment already exists. Skipping creation.')
        except PermissionError:
            print('Permission denied. Please run the script with elevated privileges.')
            exit(1)
        except Exception as e:
            print(f'Error creating virtual environment: {e}')
            exit(1)
        if install_requirements:
            requirements_file = os.path.join(self.script_dir, 'requirements.txt')
            if not os.path.exists(requirements_file):
                print('requirements.txt not found. Please create a requirements.txt file in the root directory.')
                print('Not automatically installing requirements...')
            try:
                result = subprocess.check_output([f'{full_dir}/bin/pip', 'install', '-r', requirements_file], text=True)
            except subprocess.CalledProcessError as e:
                print(f'Error: {e}')
                print('There was an error installing the requirements. Please check the error message and try again.')
                exit(1)
            if 'Successfully installed' in result:
                print('Requirements installed successfully.')
            elif 'Requirement already satisfied' in result:
                print('Requirements already installed. Skipping installation.')
            else:
                print('Error installing requirements.')
                print(result)
                print('Please check the error message and try again.')
                exit(1)
                
    def install(self, install_dir: str = '/usr/local/lib/callerid'):
        '''
        install is a function that installs the Pi-Star CallerID application.
        
        Parameters:
            None
            
        '''
        print(f'Installing Pi-Star CallerID in {install_dir}...')
        if os.path.exists(install_dir):
            print(f'Install directory {install_dir} already exists.')
            remove_files = input('Would you like to remove the existing files? (y/n): ')
            remove_files = True if remove_files.lower() == 'y' else False
            if remove_files:
                try:
                    if install_dir not in ['/usr/local/lib/callerid', '/root/callerid', '/home/pi-star/callerid', '/opt/callerid']:
                        print('Install directory is not in a safe location to delete. Exiting...')
                        exit(1)
                    subprocess.run(['rm', '-rf', install_dir], check=True)
                    print('Removed existing files from install directory.')
                except subprocess.CalledProcessError as e:
                    print(f'Error: {e}')
                    print('There was an error removing the files. Please check the error message and try again.')
                    exit(1)
        self.create_venv(install_dir)
        try:
            subprocess.run(['cp', '-r', '..', install_dir], check=True)
            print('Copied files to install directory.')
            os.makedirs(self.tmpfs_dir, exist_ok=True)
            with open ('/etc/fstab', 'a') as f:
                f.write(f'tmpfs {self.tmpfs_dir} tmpfs nodev,noatime,nosuid,mode=0755,size=10m 0 0\n')
            subprocess.run(['mount', '-a'], check=True)
            print('Created temporary directory for log files.')
            subprocess.run(['cp', f'{self.script_dir}/callerid.service', '/etc/systemd/system/callerid.service'], check=True)
            print('Copied service file to /etc/systemd/system.')
            subprocess.run(['systemctl', 'daemon-reload'], check=True)
            print('Reloaded systemd daemon, Pi-Star CallerID now available as a service.')
            self.iptables_rules = [self.api_port, self.web_port]
            for rule in self.iptables_rules:
                try:
                    subprocess.run(['iptables', '-A', 'INPUT', '-p', 'tcp', '--dport', rule, '-j', 'ACCEPT'], check=True)
                    print(f'Added iptables rule for port {rule}.')
                except subprocess.CalledProcessError as e:
                    print(f'Error: {e}')
                    print('There was an error adding the iptables rule. Please check the error message and try again.')
                    print('You may need to add the iptables rule manually or iptables may not be installed.')
        except PermissionError:
            print('Permission denied. Please run the script with elevated privileges.')
            exit(1)
        except subprocess.CalledProcessError as e:
            print(f'Error: {e}')
            print('There was an error copying the files. Please check the error message and try again.')
            exit(1)
        except Exception as e:
            print(f'Error: {e}')
            print('An unknown error occurred. Please check the error message and try again.')
            exit(1)
        print('Pi-Star CallerID installed successfully.')
        print('To start the Pi-Star CallerID application, run the following commands:')
        print('sudo systemctl start Pi-Star CallerID')
        print('To enable the Pi-Star CallerID application on boot, run the following command:')
        print('sudo systemctl enable Pi-Star CallerID')
        
if __name__ == '__main__':
    '''
    Main function that runs the installer when the script is executed directly vs. being imported.
    '''
    installer = Installer()
    print('Pi-Star CallerID Installer')
    print(dir(installer))
    input('Press Enter to continue...')
    installer.install()
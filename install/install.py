import venv
import subprocess
import os

if os.geteuid() != 0:
            print('Please run the script with elevated privileges.')
            exit(1)

def create_venv(venv_parent_dir: str, install_requirements: bool = True):
    '''
    create_venv is a function that creates a virtual environment for the Parrot application.
    
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
        global script_dir
        script_dir = os.path.dirname(os.path.realpath(__file__))
        requirements_file = os.path.join(script_dir, 'requirements.txt')
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
            
def install(install_dir: str = '/usr/local/lib/parrot'):
    '''
    install is a function that installs the Parrot application.
    
    Parameters:
        None
        
    '''
    create_venv(install_dir)
    try:
        global script_dir
        subprocess.run(['cp', '-r', '..', install_dir], check=True)
        subprocess.run(['cp', f'{script_dir}/parrot.service', '/etc/systemd/system/parrot.service'], check=True)
        subprocess.run(['systemctl', 'daemon-reload'], check=True)
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
    print('Parrot installed successfully.')
    print('To start the Parrot application, run the following commands:')
    print('sudo systemctl start parrot')
    print('To enable the Parrot application on boot, run the following command:')
    print('sudo systemctl enable parrot')
        
if __name__ == '__main__':
    print('Installing Parrot...')
    
    install()
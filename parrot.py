import json
import os
import glob
from collections import deque

'''
Parrot is a class that reads a log file and returns the log lines based on the number of lines and a filter string.

The Parrot class reads the config.json file in the root directory and sets the configuration values as attributes of the class.
This class is used as the base class for the API and Web classes to read the log files and return the log lines in real-time using Server-Sent Events (SSE).

Parameters:
    None

Methods:
    read_log: A method that reads the log file and returns the log lines based on the number of lines and a filter string

Variables:
    config: A dictionary that stores the configuration values from the config.json file
    log_directory: A string that represents the directory where the log files are stored
    log_file: A string that represents the log file name
    debug: A boolean value that represents whether debug mode is enabled

Returns:
    None

Exceptions:
    FileNotFoundError: An exception that is raised when the log files are not found
'''

class Parrot:
    def __init__(self):
        '''
        Parrot constructor that reads the config.json file and sets the configuration values as attributes of the class.
        
        Parameters:
            None
        
        Variables:
            config: A dictionary that stores the configuration values from the config.json file
        
        Returns:
            None
        '''
        self.config = json.load(open('config.json')) if 'config.json' in os.listdir() else None
        if self.config is None:
            print('config.json not found. Please create a config.json file in the root directory.')
            exit(1)
        for key in self.config:
            setattr(self, key, self.config[key])
            # Convert string to boolean for boolean values
            if self.config[key] == "True":
                setattr(self, key, True)
            elif self.config[key] == "False":
                setattr(self, key, False)
        if self.debug == True:
            print(f'{key}: {self.config[key]}')
        
        
    def read_log(self, lines: int = None, filter: str = None, log_override: str = None):
        '''
        read_log is a method that reads the log file and returns the log lines based on the number of lines and a filter string.
        
        Uses deque to store the last lines read from the log file and returns the log lines based on the number of lines and a filter string.
        
        Parameters:
            lines: An integer that represents the number of lines to read from the log file
            filter: A string that represents the filter to apply to the log lines
        
        Variables:
            files: A list of strings that represent the log files in the log directory
            newest_file: A string that represents the newest log file
            last_lines: A deque object that stores the last lines read from the log file
        
        Returns:
            generator: A generator that yields the log lines
            
        Exceptions:
            FileNotFoundError: An exception that is raised when the log files are not found
        '''
        if log_override is not None:
            self.log_file = log_override
        # Find all files that contain self.log_file in their name
        files = glob.glob(f'{self.log_directory}/{self.log_file}*')

        # If no files were found, raise an exception
        if not files:
            raise FileNotFoundError(f'No files found that contain "{self.log_file}" in their name')

        # Find the newest file
        newest_file = max(files, key=os.path.getctime)

        with open(newest_file, 'r') as f:
            last_lines = deque(f, maxlen=lines)
            for line in last_lines:
                if filter is not None:
                    if filter in line:
                        yield line.strip()
                    else:
                        continue
                else:
                    yield line.strip()
        
        if log_override is not None:
            self.log_file = self.config['log_file']

        
if __name__ == '__main__':
    '''
    This block of code is used to run the Parrot application as a standalone application.
    '''
    p = Parrot()
    lines = p.read_log(int(input('Enter number of lines to read: ')), input('Enter a filter string: '))
    print('\n'.join(lines))
    
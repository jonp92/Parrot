import json
import os
from collections import deque

class Parrot:
    def __init__(self):
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
        
        
    def read_log(self, lines: int = None, filter: str = None):
        with open(self.log_file, 'r') as f:
            last_lines = deque(f, maxlen=lines)
            for line in last_lines:
                if filter is not None:
                    if filter in line:
                        yield line.strip()
                    else:
                        continue
                else:
                    yield line.strip()

        
if __name__ == '__main__':
    p = Parrot()
    lines = p.read_log(int(input('Enter number of lines to read: ')), input('Enter a filter string: '))
    print('\n'.join(lines))
    
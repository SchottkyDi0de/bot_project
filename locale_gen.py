import os
from time import sleep

from colorama import Fore, Back, Style, init

init(autoreset=True)

# datamodel-codegen args
INPUT = 'locales/en.yaml'
INPUT_FILE_TYPE = 'yaml'
OUTPUT = 'model.py'

# internal settings
TARGET_DATACLASS_FILE = 'lib/data_classes/locale_struct.py'
RENAME_MODEL_TO = 'Localization'
FINISH_MESSAGE = 'ALL DONE!'
TOOL_NAME = f'{Fore.CYAN}Locale tool{Fore.RESET}: '

def empty_line_handler(data: list[str], index: int) -> bool:
    if data[index] == '\n':
        try:
            if data[index+1].startswith('class'):
                return False
            elif data[index+2].startswith('class'):
                return False
            return True
        except IndexError:
            return False
    
print(f'{TOOL_NAME}{Fore.YELLOW}attempt to call {Style.BRIGHT}datamodel-codegen{Style.NORMAL}')
os.system(f'datamodel-codegen --input {INPUT} --output {OUTPUT} --input-file-type {INPUT_FILE_TYPE}')

print(f'{TOOL_NAME}{Fore.YELLOW}attempt to read model.py')
with open(OUTPUT, 'r', encoding='utf-8') as f:
    data = f.readlines()

data_copy = data.copy()
for count, line in enumerate(data_copy):
    print(f'\r{TOOL_NAME}{Fore.MAGENTA}read line: {Fore.RED}{count+1}{Fore.RESET}', end='')
    if line == 'from __future__ import annotations\n':
        data[count] = '#RM_KEY\n'
        
    elif line == 'class Model(BaseModel):\n':
        data[count] = f'class {RENAME_MODEL_TO}(BaseModel):\n'
    
    elif line.startswith('#'):
        data[count] = '#RM_KEY\n'
        
    sleep(0.001)

with open(TARGET_DATACLASS_FILE, 'w', encoding='utf-8') as f:
    for count, line in enumerate(data):
        print(f'\r{TOOL_NAME}{Fore.GREEN}writing line: {Fore.RED}{count+1}{Fore.RESET}', end='')
        if data[count] == '#RM_KEY\n':
            continue
        
        if empty_line_handler(data, count):
            continue
        
        f.write(line)
        sleep(0.001)
    
    print(f'\n{TOOL_NAME}{Fore.GREEN}read / write complete!')


print(f'{TOOL_NAME}{Fore.RESET}{Back.GREEN}{FINISH_MESSAGE}{Style.RESET_ALL}')
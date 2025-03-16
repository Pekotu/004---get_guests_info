
import sys
import os
from pathlib import Path
import time

project_folder = Path(__file__).parent.parent.resolve() 

def log_to_file(message):
    with open(f"{project_folder}/send_link/Send_link1-LOG.log", 'a', encoding='utf-8') as f:
        f.write(f"{time.strftime('%d-%m-%Y %H:%M:%S', time.gmtime())} - {message} \n")

    with open(f"{project_folder}/send_link/Send_link1-LOG.log", 'r', encoding='utf-8') as f1:
        
        #lines = f1.readlines()
        lines = f1.readlines()
        if len(lines) > 10000:
            
            with open(f"{project_folder}/send_link/Send_link1-LOG.log", 'w', encoding='utf-8') as f2:
                f2.write(f"{time.strftime('%d-%m-%Y %H:%M:%S', time.gmtime())} - Log file was cleared \n")
                f2.write("-------------------------------------------- \n")
                f2.writelines(lines[2000:])
                f2.write("\n")

if __name__ == '__main__':
    pass
    #log_to_file("Test message")

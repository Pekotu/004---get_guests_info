import time

def log_to_file(message):
    with open("WEBapp-LOG.log", 'a', encoding='utf-8') as f:
        f.write(f"{time.strftime('%d-%m-%Y %H:%M:%S', time.gmtime())} - {message} \n")

    with open("WEBapp-LOG.log", 'r', encoding='utf-8') as f1:
        if len(f1.readlines()) > 10000:
            
            with open("WEBapp-LOG.log", 'w', encoding='utf-8') as f2:
                f2.write(f"{time.strftime('%d-%m-%Y %H:%M:%S', time.gmtime())} - Log file was cleared \n")
                f2.write("-------------------------------------------- \n")
                f2.writelines(f1.readlines()[2000:])
                f2.write("\n")

if __name__ == "__main__":
    pass
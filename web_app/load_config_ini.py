###############################
def load_config_ini():
    #Load configuration from config.ini file
    # number_of_attempts - number of attempts in checked_interval to block the IP address
    # checked_interval - If the IP address has sent a request more than 3 times in the last x=checked_interval minutes, it will be blocked for blocked_interval minutes
    # blocked_interval - How long the IP address will be blocked in minutes
    # If the configuration is not set, the default values are used
     
    number_of_attempts = None
    checked_interval = None
    blocked_interval = None

    with open("config.ini", "r", encoding="utf-8") as f:
        configs = f.readlines()
    
    #find configuration in lines
    for line in configs:
        line = line.strip()
        if line == "":
            continue

        if line[0] == "#" or line == "": # skip comments and empty lines    
            continue

        line = line.split("#")[0] # remove comments from end of line  
        line = line.replace(" ", "") # remove spaces
        
        #eliminate values which are not numbers
        try:
            if line.startswith('number_of_attempts='):
                number_of_attempts = int(line.split('=')[1])
        except:
            number_of_attempts = None

        try:
            if line.startswith('checked_interval='):
                checked_interval = int(line.split('=')[1])
        except:
            checked_interval = None

        try:
            if line.startswith('blocked_interval='):
                blocked_interval = int(line.split('=')[1])
        except:
            blocked_interval = None            

        try:
            if line.startswith('use_for_apartments='):
                use_for_apartments = line.split('=')[1].split(',')
                if use_for_apartments == ['all']:
                    use_for_apartments = ['all']
                else:    
                    use_for_apartments_clear = [str(x).replace(" ", "") for x in use_for_apartments if str(x).replace(" ", "").isdigit()]
                    use_for_apartments = use_for_apartments_clear

        except:
            use_for_apartments = None



        if number_of_attempts == '' or number_of_attempts == None or number_of_attempts==0:
            number_of_attempts = 3

        if checked_interval == '' or checked_interval == None or checked_interval==0:
            checked_interval = 5
        
        if blocked_interval == '' or blocked_interval == None or blocked_interval==0:
            blocked_interval = 20
        

    return number_of_attempts, checked_interval, blocked_interval, use_for_apartments


if __name__ == "__main__":
    pass
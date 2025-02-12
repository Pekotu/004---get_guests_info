import sys
import os
from pathlib import Path

project_folder = Path(__file__).parent.parent.resolve() 
print(project_folder)

sys.path.append(os.path.abspath(f"{project_folder}/translate") )

from pk_translate import *

from send_email.send_smtp_email import send_smtp_email
from send_sms import send_sms
import time
from pathlib import Path

import os
import logging
import json
#import fcntl
from db_send_link import * 
import ast




################################################

def send_link(record):
    
    phone = record.get('phone')
    email = record.get('email')
    webhook = ast.literal_eval(record.get('webhook'))
    language = record.get('language')
    name = webhook.get('guest_name')
    apartment = webhook.get('property_name')
    booking_id = webhook.get('id')


    #---odesle zpravu o kazdém Hooku na muj email----------------------------
    predmet2 = f"přijatý HOOK {booking_id=}"
    email2 = "petr@kopeckysolution.com"
    msg=f'https://pkopecky.pythonanywhere.com/identification/{booking_id}'

    #send email
    email_result = send_smtp_email(predmet2, msg, email2)

    #record['link_sent_at'] = time.strftime('%d-%m-%Y %H:%M:%S')


    #---------------------------------

    #*********** TEST *********************
    if webhook.get('test') == "test":
    #*********** TEST *********************


        #send email to customer
        if email == "kopeckysolution@seznam.cz" or email == "ahoj@janpokorny.cz":

            #-------
            # Formate dates to d.m.y
            # Assuming 'check_in' contains a date in the format 'YYYY-MM-DD'
            date_start = datetime.strptime(webhook['check_in'], '%Y-%m-%d')
            date_end = datetime.strptime(webhook['check_out'], '%Y-%m-%d')

            # Formatting the date to format d.m.y
            date_start = str(date_start.strftime('%d.%m.%Y'))
            date_end = str(date_end.strftime('%d.%m.%Y'))

            #-------

            link = f'https://hv.kopeckysolution.com/identification/{booking_id}'

            
            content = translate_content("email", webhook, language )

            
            msg = content['text'].format(xlinkx = link, xnamex = name, xapartmentx = apartment, xdate_startx = date_start, xdate_endx = date_end)
            subject = content['subject'].format(xapartmentx = apartment)
            

            # send message to email
            if email != None:
                email_result = send_smtp_email(subject, msg, email)

            if email_result == 'ok':
                add_send_link_email_to_db(booking_id)
                log_to_file(f"Email sent to {email}")
               
            else:
                add_send_link_email_error_to_db(booking_id)
                log_to_file(f"ERROR - Email sent to {email}")

            #SMS SMS SMS
            if phone != "000":
                pass
                response = 'ok'
                #response = send_sms(phone, msg)

            else:
                response = 'ok'    

            if response == 'ok':
                add_send_link_sms_to_db(booking_id)
                log_to_file(f"SMS sent to {phone}")

            else:
                add_send_link_sms_error_to_db(booking_id)
                log_to_file(f"ERROR - SMS sent to {phone}")
            
    return


##################################
def log_to_file(message):
    with open("mujLOG.txt", 'a', encoding='utf-8') as f:
        f.write(f"{time.strftime('%d-%m-%Y %H:%M:%S', time.gmtime())} - {message} \n")
        
###################################
if __name__ == '__main__':

    log_to_file('Start - send_link.py')
    
    # Open a file and get a lock
    # evaoid multiple instances of this program
    #lockfile = open('/tmp/send_link.lock', 'w')

    try:
        # try to get an exclusive lock to evoid multiple instances
        #fcntl.flock(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        log_to_file('NEW Start - send_link.py')
    
    except BlockingIOError:
        # If the file is already locked, exit
        log_to_file("Program is already running")
        sys.exit(0)

    while True:
        # in the loop, it fetches webhooks from the db that have not been sent yet
        # send an email and sms with a link to customers
        log_to_file('Start loop')
        
        # load all hooks which has not send link
        not_sent_hooks = select_hooks_with_not_sent_link()
        
        log_to_file(f'HOOKS to SEND LINK= {not_sent_hooks}')

        for hook in not_sent_hooks:
            send_link(hook)

        log_to_file('End loop')
        time.sleep(30)

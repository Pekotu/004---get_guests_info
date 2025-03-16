import sys
import os
from pathlib import Path

project_folder = Path(__file__).parent.parent.resolve() 
#print(project_folder)

sys.path.append(os.path.abspath(f"{project_folder}/translate") )

from pk_translate import *
from send_email.send_smtp_email import send_smtp_email
from send_sms import send_sms
import time
from pathlib import Path
import os
import logging
import json
from db_send_link import * 
import ast
import configparser


################################################

#send email to owner
def send_email_owner(record):
    try:
        if email_owner != None and email_owner != '':
            webhook = ast.literal_eval(record.get('webhook'))
            booking_id = webhook.get('id')

            subject_owner = f"přijatý HOOK {booking_id=}"
            #email_owner = "petr@kopeckysolution.com"
            msg_owner=f'Přijatý HOOK: {webhook}'

            #send email
            email_result = send_smtp_email(subject_owner, msg_owner, email_owner)
            
            if email_result == 'ok':
                    try:
                        add_send_info_to_owner_to_db(booking_id)
                        log_to_file(f"send_link - {booking_id=}- Email sent to OWNER = OK - add to DB = OK")
                    except Exception as e:
                        log_to_file(f"send_link - {booking_id=}- Email sent to OWNER = OK - add to DB = ERROR: {e}")  
    
    except Exception as e:
        log_to_file(f"send link to owner - {booking_id=} - ERROR: {e}")
        

    return

######################################
def send_link_email_customer(record):
    try:
        email = record.get('email')
        webhook = ast.literal_eval(record.get('webhook'))
        language = record.get('language')
        name = webhook.get('guest_name')
        apartment = webhook.get('property_name')
        booking_id = webhook.get('id')
        
        link = load_link(booking_id) 
        
        # Formate dates to d.m.y
        date_start, date_end = format_dates_for_message(webhook)

        #translate content
        content = translate_content("email", webhook, language )
        
        #insert vales to email template
        msg = content['text'].format(xlinkx = link, xnamex = name, xapartmentx = apartment, xdate_startx = date_start, xdate_endx = date_end)

        subject = content['subject'].format(xapartmentx = apartment)

        # send message to customer email
        email_result = send_smtp_email(subject, msg, email)

        if email_result == 'ok':
            add_send_link_email_to_db(booking_id)
            log_to_file(f"send_link - {booking_id=} - Email sent to {email=}")
            
        else:
            add_send_link_email_error_to_db(booking_id)
            log_to_file(f"send_link - {booking_id=} - ERROR - Email sent to {email=}")

    except Exception as e:
        log_to_file(f"send link - {booking_id=} - to customer - ERROR: {e}")
        add_send_link_email_error_to_db(booking_id)

    return


######################################
def send_link_sms_customer(record):
    try:    
        phone = record.get('phone')
        webhook = ast.literal_eval(record.get('webhook'))
        language = record.get('language')
        name = webhook.get('guest_name')
        apartment = webhook.get('property_name')
        booking_id = webhook.get('id')
        
        link = load_link(booking_id) 

        date_start, date_end = format_dates_for_message(webhook)

        content = translate_content("sms", webhook, language )
        
        msg = content['text'].format(xlinkx = link, xnamex = name, xdate_startx = date_start, xdate_endx = date_end)

        msg = msg.replace('<br>', '\n')
        
        # Remove diacritics from msg
        msg = remove_diacritic_replace(msg)
        
        #send sms to customer phone
        response = send_sms(phone, msg)
        
        if str(response) == "<Response [200]>":    
            log_to_file(f"sms send - {booking_id=} - OK - {response=}")
            add_send_link_sms_to_db(booking_id)

        else:
            log_to_file(f"sms send - {booking_id=} - ERROR - {response=}")
            add_send_link_sms_error_to_db(booking_id)

    except Exception as e:
        log_to_file(f"send link - {booking_id=} - sms_customer - ERROR: {e}")
        add_send_link_sms_error_to_db(booking_id)

    return

######################################
def remove_diacritic_replace(text):
    diakritika =     "áčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ"
    bez_diakritiky = "acdeeinorstuuyzACDEEINORSTUUYZ"
    trans = str.maketrans(diakritika, bez_diakritiky)
    return text.translate(trans)


######################################
def format_dates_for_message(webhook):
# Formate dates to d.m.y
    # Assuming 'check_in' contains a date in the format 'YYYY-MM-DD'
    date_start = datetime.strptime(webhook['check_in'], '%Y-%m-%d')
    date_end = datetime.strptime(webhook['check_out'], '%Y-%m-%d')

    # Formatting the date to format d.m.y
    date_start = str(date_start.strftime('%d.%m.%Y'))
    date_end = str(date_end.strftime('%d.%m.%Y'))

    return (date_start, date_end)



######################################
def load_link(booking_id):
    return f'https://api.homevibes.cz/ide/{booking_id}'



##################################
def log_to_file(message):
    
    log_file_path = f"{project_folder}/send_link/Send_link-LOG2.log"

    with open(log_file_path, 'a', encoding='utf-8') as f:
        f.write(f"{time.strftime('%d-%m-%Y %H:%M:%S', time.gmtime())} - {message} \n")
        

    with open(log_file_path, 'r', encoding='utf-8') as f1:
        if len(f1.readlines()) > 10000:
            
            with open(log_file_path, 'w', encoding='utf-8') as f2:
                f2.write(f"{time.strftime('%d-%m-%Y %H:%M:%S', time.gmtime())} - Log file was cleared \n")
                f2.write("-------------------------------------------- \n")
                f2.writelines(f1.readlines()[2000:])
                f2.write("\n")


###################################
if __name__ == '__main__':

    log_to_file('''------------- NEW Start of Aplication - send_link2.py --------------''')
    
    # load config.ini
    config = configparser.ConfigParser()
    config.read(f"config.ini")

    # interval_to_send_links = int(config['settings']['interval_to_send_links'])
    # send_email_to_owner = config['settings']['send_email_to_owner'].lower()
    # email_owner = config['settings']['email_owner']
    # send_email_to_customer = config['settings']['send_email_to_customer'].lower()
    # send_sms_to_customer = config['settings']['send_sms_to_customer'].lower()

    interval_to_send_links = 30
    send_email_to_owner = 'true'
    email_owner = "kopeckysolution@seznam.cz"
    send_email_to_customer = 'true'
    send_sms_to_customer = 'true'


    # log_to_file(f"{interval_to_send_links=}")
    # log_to_file(f"{send_email_to_owner=}")
    # log_to_file(f"{email_owner=}")
    # log_to_file(f"{send_email_to_customer=}")
    # log_to_file(f"{send_sms_to_customer=}")

    # True or False
    send_email_to_owner = 'true'

    # email address of the owner
    email_owner = "petr@kopeckysolution.com"

    # True or False
    send_email_to_customer = 'true'

    # True or False
    send_sms_to_customer = 'true'
    
    # in the loop, it fetches webhooks from the db that have not been sent yet
    # send an email and sms with a link to customers
    while True:    
        log_to_file('Start loop2')

        ##########
        #send email to owner        
        if send_email_to_owner == 'true': 
            
            # load all hooks which has not send link to owner
            not_sent_records = select_records_not_sent_to_owner()
            
            for record in not_sent_records:
                #send_email_owner(record)
                log_to_file(f"send_link - {record.get('webhook')} - Email sent to OWNER = OK - add to DB = OK")

        ##########
        # send email to customer
        if send_email_to_customer == 'true':
            
            # load all hooks which has not send link tp customer email
            not_sent_records = select_records_with_not_sent_link_email()
            

            for record in not_sent_records:
                #send_link_email_customer(record)        
                log_to_file(f"send_link - {record.get('webhook')} - Email sent to customer = OK - add to DB = OK")

        ##########
        # send SMS to customer
        if send_sms_to_customer == 'true':
            
            # load all hooks which has not send link tp customer email
            not_sent_records = select_records_with_not_sent_link_sms()
            

            for record in not_sent_records:
                #send_link_sms_customer(record)        
                log_to_file(f"send_link - {record.get('webhook')} - SMS sent to customer = OK - add to DB = OK")
        
        log_to_file('End loop2')
        time.sleep(interval_to_send_links)
        
            
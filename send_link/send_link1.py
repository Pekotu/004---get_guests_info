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
#import logging
import json
from db_send_link import * 
import ast
import configparser
from datetime import datetime, timedelta
from log_to_file import log_to_file
from load_apartments_spec import load_apartments_spec


################################################

#send email to owner
def send_webhook_to_owner(record, email_owner):
    
    try:
        if email_owner:
            webhook = ast.literal_eval(record.get('webhook'))
            booking_id = webhook.get('id')
            
            log_to_file(f"send link to owner - {booking_id=} - {email_owner=}")

            subject_owner = f"přijatý HOOK {booking_id=}"
            msg_owner=f'Přijatý HOOK: {webhook}'

            #send email to programmer
            email_result = send_smtp_email(subject_owner, msg_owner, "petr@kopeckysolution.com")
            log_to_file(f"send link to owner - {booking_id=}- Email sent to PROGRAMMER = {email_result}")
            
            #send email to owner
            email_result = send_smtp_email(subject_owner, msg_owner, email_owner)
            log_to_file(f"send link to owner - {booking_id=}- Email sent to OWNER = {email_result}")
                        
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
def prepare_message(record, message_category, email_sms):
    
    email = record.get('email')
    phone = record.get('phone')
    webhook = ast.literal_eval(record.get('webhook'))
    language = record.get('language')
    name = webhook.get('guest_name')
    booking_id = webhook.get('id')
    
    property_name = int(webhook.get('property_name').replace(' ', ''))
    apartment_spec = apartments_spec.get(property_name)
    if apartment_spec == None:
        add_send_message_error_to_db(booking_id, message_category, email_sms)
        log_to_file(f"prepare_message - {booking_id=} - {message_category=} - {email_sms=} - {property_name} - ERROR: Apartment specification not found")
        return None
    apartment = apartment_spec.get('Popis_formulář')
    general_info_link = apartment_spec.get('Obecné info')
    arrival_info_link = apartment_spec.get('Check-in info')
    link = f'https://api.homevibes.cz/ide/{booking_id}' 

    # Formate dates to d.m.y
    date_start, date_end = format_dates_for_message(webhook)

    #translate content
    content = translate_content(f'{email_sms}_{message_category}', webhook, language )
    
    #insert vales to email template
    for key in content:
        content[key] = content[key].format(xnamex = name, xapartmentx = apartment, xdate_startx = date_start, xdate_endx = date_end, xlinkx = link, xgeneral_info_linkx = general_info_link, xarrival_info_linkx = arrival_info_link )

    if email_sms == 'sms':
        content['text'] = content['text'].replace('<br>', '\n')
        content['text'] = remove_diacritic_replace(content['text'])
    
    return content


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


##################################
# load config.ini
def load_config():
    global interval_to_send_links
    global send_email_to_owner
    global email_owner
    global send_email_to_customer
    global send_sms_to_customer
    global time_to_send_arrival_message
    global time_to_send_departure_message
    
    config = configparser.ConfigParser()
    config.read(f"{project_folder}/send_link/config.ini")

    try:
        interval_to_send_links = int(config['settings']['interval_to_send_links'])
        send_email_to_owner = config['settings']['send_email_to_owner'].lower()
        email_owner = config['settings']['email_owner']
        send_email_to_customer = config['settings']['send_email_to_customer'].lower()
        send_sms_to_customer = config['settings']['send_sms_to_customer'].lower()
        time_to_send_arrival_message = config['settings']['time_to_send_arrival_message']
        time_to_send_departure_message = config['settings']['time_to_send_departure_message']

    except Exception as e:
        log_to_file(f"Error loading config.ini: {e}")
        send_smtp_email('Error loading config.ini', f'Error loading config.ini: {e}', 'petr@kopeckysolution.com')
        interval_to_send_links = 30
        send_email_to_owner = 'true'
        email_owner = 'petr@kopeckysolution.com'
        send_email_to_customer = 'false'
        send_sms_to_customer = 'false'
        time_to_send_arrival_message = '15:00'
        time_to_send_departure_message = '9:00'

    log_to_file(f"{interval_to_send_links=}")
    log_to_file(f"{send_email_to_owner=}")
    log_to_file(f"{email_owner=}")
    log_to_file(f"{send_email_to_customer=}")
    log_to_file(f"{send_sms_to_customer=}")
    log_to_file(f"{time_to_send_arrival_message=}")
    log_to_file(f"{time_to_send_departure_message=}")

##################################

def send_message_to_owner():
    #send email to owner        
    if send_email_to_owner == 'true': 
        
        # load all hooks which has not send link to owner
        not_sent_records = select_records_not_sent_to_owner()
        
        for record in not_sent_records:
            send_webhook_to_owner(record, email_owner)


##################################
# Send messages to customers
def send_messages_to_customers(message_category):
    record = None
    result = None

    try:
        email_sms_list = ['email', 'sms']
        for email_sms in email_sms_list:
            not_sent_records = []
            
            #EMAIL
            if email_sms == 'email' and send_email_to_customer == 'true':
                not_sent_records = select_records_with_not_sent_message(message_category, email_sms)

                log_to_file(f"send_messages_to_customers - {message_category=} - {email_sms=} - {not_sent_records=}")
            
                #send email to customers one by one
                for record in not_sent_records:
                    content = prepare_message(record, message_category, email_sms)
                    if content == None: #special case when apartment specification is not found
                        continue

                    #do not send email if guest did not enter contacts to form in web_app
                    xx = record.get('data_from_form')
                    if message_category in ['arrival', 'departure'] and not record.get('data_from_form'):
                        log_to_file(f"send_messages_to_customers - {message_category=} - {email_sms=} - NOT SENT because data_from_form are empty")
                        break

                    #send email
                    result = None
                    result = send_smtp_email(content['subject'], content['text'], record.get('email'))
            
            #SMS
            elif email_sms == 'sms' and send_sms_to_customer == 'true':
                not_sent_records = select_records_with_not_sent_message(message_category, email_sms)

                log_to_file(f"send_messages_to_customers - {message_category=} - {email_sms=} - {not_sent_records=}")
            
                #send sms to customers one by one
                for record in not_sent_records:
                    
                    content = prepare_message(record, message_category, email_sms)
                    if content == None: #special case when apartment specification is not found
                        continue

                    #do not send email if guest did not enter contacts to form in web_app
                    xx = record.get('data_from_form')
                    if message_category in ['arrival', 'departure'] and not record.get('data_from_form'):
                        log_to_file(f"send_messages_to_customers - {message_category=} - {email_sms=} - NOT SENT because data_from_form are empty")
                        break

                    phone = record.get('phone')
                    #send sms
                    result = None
                    log_to_file(f"send_messages_to_customers - {message_category=} - {email_sms=} - Before send")
                    result = send_sms(phone, content['text'])
                    log_to_file(f"send_messages_to_customers - {message_category=} - {email_sms=} - after send - {result=}")
            
            if result:
                if record:
                    booking_id = record.get('booking_id')
                    email = record.get('email')
                    phone = record.get('phone')        
                else:
                    booking_id = 'unknown'
                    email = 'unknown'
                    phone = 'unknown'

                if result == 'ok' or str(result) == "<Response [200]>":
                    add_send_message_to_db(booking_id, message_category, email_sms)
                    log_to_file(f"send_message_to_customer - {booking_id=} - {email_sms=} - {email=} / {phone=} - OK")
                    
                else:
                    add_send_message_error_to_db(booking_id, message_category, email_sms)
                    log_to_file(f"send_message_to_customer - {booking_id=} - {email_sms=} - {email=} / {phone=} - ERROR")

    except Exception as e:
        if record: 
            booking_id = record.get('booking_id')
            add_send_message_error_to_db(booking_id, message_category, email_sms)
        else:
            booking_id = 'unknown'

        log_to_file(f"send_message_to_customer - {booking_id=} - {email_sms=} - Exception ERROR: {e}")
        



##################################
#Global variables:        
apartments_spec = {}

##################################
# Main
##################################
if __name__ == '__main__':

    log_to_file('''\n--------------------------------------------\nNEW Start of Application - send_link.py\n''')
    
    #define global variables
    interval_to_send_links = 0
    send_email_to_owner = ''
    email_owner = ''
    send_email_to_customer = ''
    send_sms_to_customer = ''
    time_to_send_arrival_message = ''
    time_to_send_departure_message = ''
    
    previous_spec_update = datetime(2000,1,1,0,0,0)
    #never ending loop
    while True:
        #load config.ini
        load_config()

        #load apartment specification once in 10 minutes
        now = datetime.now()
        if datetime.now()>= previous_spec_update + timedelta(minutes=10):
            try:
                apartments_spec = load_apartments_spec()
                previous_spec_update = datetime.now()
            except Exception as e:
                log_to_file(f"Error loading apartment specification: {e}")
                send_smtp_email('Error loading apartment specification', f'Error loading apartment specification: {e}', owner_email)
            
        # in the loop, it fetches webhooks from the db that have not been sent yet
        # send an email and sms with a link to customers
        log_to_file('Start loop')
        
        # Send message to owner
        send_message_to_owner()

        # Message - booking
        send_messages_to_customers('booking')
        
        # Message - Arrival
        # Arrival message is sent at date of arrival at time defined in config.ini
        # there is a few minutes window to send message
        current_time = datetime.strptime(time.strftime('%H:%M'), '%H:%M')
        arrival_time_start = datetime.strptime(time_to_send_arrival_message, '%H:%M')
        arrival_time_end = arrival_time_start + timedelta(minutes=10)

        if current_time > arrival_time_start and current_time < arrival_time_end:
            send_messages_to_customers('arrival')
        
        # Message - Departure
        # Departure message is sent at date of departure at time defined in config.ini
        # there is a few minutes window to send message
        departure_time_start = datetime.strptime(time_to_send_departure_message, '%H:%M')
        departure_time_end = departure_time_start + timedelta(minutes=10)
        if current_time > departure_time_start and current_time < departure_time_end:
            send_messages_to_customers('departure')
        
        log_to_file('End loop')
        time.sleep(interval_to_send_links)
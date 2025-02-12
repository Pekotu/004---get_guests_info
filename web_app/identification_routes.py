from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask import url_for
from flask import flash

import os
import time
import ast

import json

from pathlib import Path

from db import *
from log_to_file import log_to_file


project_folder = Path(__file__).parent.parent.resolve()

# add path to the folder from where modules will also be loaded

from store_data_to_googlesheet.direct_connection_to_gsheet import write_data_to_gsheet


sys.path.append(os.path.abspath(f"{project_folder}/")) 

from translate.pk_translate import *

from datetime import datetime



###############################
# ------------Identification
# ------------Identification

def register_identification_routes(app):

    app.secret_key = 'tv$$$ůj_ta%%323jný_klíč' # Required for flash messages

    # page for identification of user - user enters email or phone
    @app.route('/identification/<booking_id>') 
    def identification(booking_id):
        log_to_file(f'url={request.url}')
        log_to_file(f'{booking_id=}')
        
        #if booking_id is empty, return wrong link
        if booking_id == '' or booking_id == None:
            return wrong_link(None)

        #if id in url is not in db, return wrong link
        record = get_record_from_db(booking_id)
        if record == None:
            return wrong_link(None)

        #if record is in db, but webhook is empty, return wrong link
        webhook = ast.literal_eval(record.get('webhook', []))
        if webhook == [] or webhook == None:
            return wrong_link(None)

        log_to_file(f'{booking_id=}')
        if webhook == [] or webhook == None:
            flash('You have wrong link, use link which you received to email or sms.')
            return render_template('error.html')

        
        language = record.get('language')
        if language == None:
            language = 'CZ'
        content = translate_content(content_name='identification', webhook=webhook, language=language ) 
        # loads the content of the page and translates it to the language from the webhook
    
        return render_template('identification.html', booking_id=booking_id, content = content)

    ###############################

    # Check if data is being extracted from the application based on randomly generated numbers
    # Checks how many times the IP address has sent a request in the last 5 minutes, if it is already 3 times, it blocks the IP address for 20 minutes
    # Checks if the entered phone number and email match those to which the link was sent
    # ------------Processing Identification
    # ------------Processing Identification
    #receives data from the identification form and checks if the link was sent to the email or phone. If the link was sent, it sends the user to the form
    @app.route('/identification_submit', methods=["GET", "POST"])
    def identification_submit():

        #try: 
        reply_dict = request.form.to_dict()
        booking_id = reply_dict.get('booking_id')

        log_to_file(f'{reply_dict=}')
        log_to_file(f'{booking_id=}')

        # IP check of the user
        ip = request.remote_addr
        
        #save IP address to db
        add_ip_address_to_db(ip)
        

        # check if data is being extracted from the application based on randomly generated numbers

        # if the same IP tries to access more than 3 times in the last 5 minutes, block the IP address for 20 minutes

        checked_interval = 300 #5 minutes
        count_of_attempts = get_count_of_attempts_by_ip(ip, checked_interval)

        if count_of_attempts > 30:
            blocked_till = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() + 20*60))
            add_blocked_ip_to_db(ip, blocked_till)
            
        #Load webhook from db
        record = get_record_from_db(booking_id)
        webhook = record.get('webhook', None) 
        if webhook != '':
            webhook = ast.literal_eval(webhook)
        else:
            # If the webhook is empty, the link is wrong
            content = translate_content(content_name='identification', webhook=webhook ) 
            flash(content['wrong_link'])  
            return render_template('error.html')



        if is_ip_blocked(ip):
            content = translate_content(content_name='identification', webhook=webhook, language=record.get('language') ) 
            # loads the content of the page and translates it to the language from the webhook

            flash(content['blocked_page'])  # Flash message for user
            return render_template('error.html')
            #return redirect(url_for('error', booking_id=reply_dict['booking_id']))

        else:

            # IP is not blocked

            #Test if link was sent to this email or phone

            email = reply_dict['email'].strip()
            phone = reply_dict['phone'].strip()
            
            # empty email and phone

            if email == "" and phone == "":
                content = translate_content(content_name='identification', webhook=webhook, language=record.get('language') ) 
                # loads the content of the page and translates it to the language from the webhook
                
                # Wrong email or phone
                flash(content['empty'])  

                return redirect(url_for('identification', booking_id=reply_dict['booking_id']))


            #test if link was sent to this email or phone

            if email !="": 
                sent_link_email = was_send_link_to_email(email, booking_id)
            else:
                sent_link_email = False
            
            if phone !="": 
                sent_link_phone = was_send_link_to_phone(phone, booking_id)
            else:
                sent_link_phone = False

            # OK OK OK

            if sent_link_email or sent_link_phone:
                # OK send to form
                
                #change date format from text to datetime
                webhook['check_in_f'] = format_date(webhook['check_in'])
                webhook['check_out_f'] = format_date(webhook['check_out'])

                # loads previously saved form data
                form_data = record.get('data_from_form', None)
                if form_data : 
                    form_data_dict = ast.literal_eval(form_data)
                else:
                    form_data_dict = {}


                content = translate_content(content_name='form', webhook=webhook, language=record.get('language') ) 
                # loads the content of the page and translates it to the language from the webhook
                
                return render_template('form.html', wd = webhook, error_message = "", form_data = form_data_dict, content = content)
                
            # Wrong email or phone

            else:
                content = translate_content(content_name='identification', webhook=webhook ) 
                flash(content['wrong_value'])  

                return redirect(url_for('identification', booking_id=booking_id))
        

        #except Exception as e:

        content = translate_content(content_name='identification', webhook=webhook ) 
        flash(content['wrong_link'])  

        return render_template('error.html')

###############################
# Converts a text string to a date

def format_date(date):

    date_list = date.split("-")

    formated_date = f"{date_list[2]}.{date_list[1]}.{date_list[0]}"
    

    return formated_date

###############################
#Wrong Link
def wrong_link(webhook):
    
    log_to_file(f'Wrong Link - {webhook=}')
    if webhook == None:
        content = translate_content(content_name='identification', webhook=webhook, language='EN-GB' )
    else:
        content = translate_content(content_name='identification', webhook=webhook, language=record.get('language') ) 
    
    flash(content['wrong_link'])  
    return render_template('error.html'), 404


###############################
if __name__ == '__main__':
    
    load_apartment_name(2)




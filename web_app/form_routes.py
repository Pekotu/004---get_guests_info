
from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask import url_for
from flask import flash


import os
import time
import json
import sys
from pathlib import Path

import ast
from datetime import datetime
from db import *
from log_to_file import log_to_file


project_folder = Path(__file__).parent.parent.resolve()
script_folder = Path(__file__).parent.resolve()
sys.path.append(os.path.abspath(f"{script_folder}/store_data_to_googlesheet/")) 
#adds path to the folder from which modules will also be loaded
from store_data_to_googlesheet.direct_connection_to_gsheet import write_data_to_gsheet

sys.path.append(os.path.abspath(f"{project_folder}/")) 
from translate.pk_translate import *


################################################################################
################################################################################
#-------------form
#-------------form
def register_form_routes(app):

    app.secret_key = 'tv$$$ůj_ta%%323jný_klíč' 
    
    #-------------receiving data from the form
    form_data = {}
    @app.route('/', methods=["GET", "POST"])
    def submit_form():

        get_data_paths()
        log_to_file('route_form: submit_form')
        
        form_data = request.form.to_dict()
        
        log_to_file(f'{form_data=}')

        content = translate_content('form', webhook={} , language='cs' )

        # if form_data == None:
        #     flash(content['error']) 
        #     return render_template('error.html')

        webhook_data = form_data.get('webhook_data')
        if webhook_data != None:
            webhook_data = ast.literal_eval(webhook_data)
        else:
            return
            # flash(content['error']) 
            # return render_template('error.html')

        language = get_record_from_db(webhook_data['id']).get('language')

        content = translate_content('form', webhook= webhook_data, language=language )
        # Load the content of the page and translate it into the language from the webhook

        record = get_record_from_db(webhook_data['id'])
        #try:
        if form_data.get('id') != None:
            ##
            # Validate received data from form
            error_message = ""

            #load previous errors from form
            errors_from_form = record.get('errors_from_form', {}) 
            if errors_from_form != {}:
                errors_from_form = ast.literal_eval(errors_in_form)

            # Check validity of data from form
            error_message, errors_from_form = check_validity_of_data(form_data, content, errors_from_form)
            
            # Save summary errors from form to database
            form_data['errors_from_form'] = errors_from_form
            if error_message:    
                return render_template('form.html', wd = webhook_data, error_message = error_message, form_data = form_data, content = content)

            # add timestampu when data were stored
            form_data['form_data_stored_at'] = time.strftime("%d-%m-%Y %H:%M:%S")  

            # Counting how many times the form data has been saved for one booking_id 
            scounter = int(form_data.get('counter_of_saving',0) )

            form_data['counter_of_saving'] = scounter + 1

            #removal of webhook_data from form_data
            form_data.pop('webhook_data', None)

        
            # Save data from form to Database
            add_data_from_form_to_db(form_data.get('id'), form_data)

            # Save data from form to Google Sheet
            form_data['apartman'] = webhook_data['property_id']
            form_data['check_in'] = webhook_data['check_in']
            form_data['check_out'] = webhook_data['check_out']
            form_data['channel'] = webhook_data['channel']
            form_data['booked_at'] = webhook_data['booked_at']
            form_data['booked_by'] = webhook_data['guest_name']
            form_data['booked_by_phone'] = webhook_data['guest_phone']
            form_data['booked_by_email'] = webhook_data['guest_email']
            
            result = write_data_to_gsheet(form_data, errors_from_form)

            #print(result)
            flash(content['saved'])
            return render_template('finish.html')

        else:
            flash(content['error']) 
            return render_template('error.html')



        # except TypeError as e:
        #     log_to_file(f"Error - exceptionin -def submit_form-: {e}")
        #     content = translate_content('error', webhook= webhook_data, language=language ) #načte obsah stránky a přeloží do jazyka z webhooku   
        #     flash(content['error'])  # Flash zpráva pro uživatele
        #     return render_template('error.html')


    ###############################
    # GDPR

    @app.route('/gdpr') 
    def gdpr():
        
        return render_template('gdpr2.htm')


###############################
# Check validity of data from form
#If data are not valid, return error message
#results are saved to google sheet
def check_validity_of_data(form_data, content, errors_in_form):
    error_message = ""
    adults = 0
    for key in form_data:
        if "phone" in key:
            #international phone code
            with open(phone_international_codes_path, "r", encoding="utf-8") as file:
                icodes = file.read() #file.readlines()

            phone = form_data.get(key).replace(" ", "").replace("-", "").replace(".", "").replace(",", "")
            
            icode = None
            #phone prefix
            for i in range(2, 5):
                if phone[:i] + "\n" in icodes and phone.startswith('+'):
                    icode = phone[:i]
            
                    #test phone length
                    if len(phone)-len(icode) < 7:
                        error_message += f"{content['phone_length']}<br>"
                        errors_in_form['phone_length'] = errors_in_form.get('phone_length', 0) + 1
                        
                    break

            if not(icode):
                error_message += f"{content['phone_prefix']}<br>"
                errors_in_form['phone_prefix'] = errors_in_form.get('phone_prefix', 0) + 1
                
        elif "first_name" in key:    
            #First Name
            if len(form_data.get(key)) < 2:
                error_message += f"{content['first_name_length']}<br>" 
                errors_in_form['first_name_length'] = errors_in_form.get('first_name_length', 0) + 1
            
            if not form_data.get(key).isalpha():
                error_message += f"{content['first_name_format']}<br>"
                errors_in_form['first_name_format'] = errors_in_form.get('first_name_format', 0) + 1

        elif "family_name" in key:        
            #Family Name
            if len(form_data.get(key)) < 3:
                error_message += f"{content['family_name_length']}<br>" 
                errors_in_form['family_name_length'] = errors_in_form.get('family_name_length', 0) + 1
            
            if not form_data.get(key).isalpha():
                error_message += f"{content['family_name_format']}<br>"
                errors_in_form['family_name_format'] = errors_in_form.get('family_name_format', 0) + 1

        elif "passport" in key:
            if len(form_data.get(key)) < 5:
                error_message += f"{content['id_length']}<br>"   
                errors_in_form['id_length'] = errors_in_form.get('id_length', 0) + 1      

        elif "street" in key:
            if len(form_data.get(key)) < 3:
                error_message += f"{content['street_length']}<br>"
                errors_in_form['street_length'] = errors_in_form.get('street_length', 0) + 1

        elif "town" in key:
            if len(form_data.get(key)) < 3:
                error_message += f"{content['town_length']}<br>"
                errors_in_form['town_length'] = errors_in_form.get('town_length', 0) + 1   

        elif "country" in key:
            if len(form_data.get(key)) < 3:
                error_message += f"{content['country_length']}<br>" 
                errors_in_form['country_length'] = errors_in_form.get('country_length', 0) + 1

        elif "birthday" in key:

            birthday = datetime.strptime(form_data.get(key), '%Y-%m-%d')
            today = datetime.today()
            days = (today - birthday).days

            if days >= 18 * 365:
                adults += 1
            
            if birthday.year < 1900 or birthday.year > today.year:
                error_message += f"{content['birthday_year']}<br>"
                errors_in_form['birthday_year'] = errors_in_form.get('birthday_year', 0) + 1

                

    if adults == 0:
        error_message += f"{content['adult']}<br>"
        errors_in_form['adult'] = errors_in_form.get('adult', 0) + 1
    return error_message, errors_in_form



###############################
# get DATA folders paths
def get_data_paths():

    # Setting file paths
    global phone_international_codes_path # cesta k souboru s mezinárodnímu předvolbami telefonních čísel
    
    # Get the path to the currently running script
    script_path = os.path.abspath(__file__)
    # Get the path to the directory where the script is located
    slozka_skriptu = os.path.dirname(script_path)
    # Get the path to the parent directory
    nadrazena_slozka = os.path.dirname(slozka_skriptu)
    # Paths to the DATA directory
    data_path= os.path.join(nadrazena_slozka, "data")

    # Path to the file with international phone codes
    phone_international_codes_path = os.path.join(nadrazena_slozka,"translate","phone_international_codes", 'phone_international_codes.txt') 
    
    return

if __name__ == "__main__":
    pass

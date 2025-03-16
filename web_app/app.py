################################
##### příjem webhooku
################################

#documentation of api uplisting
# https://documenter.getpostman.com/view/1320372/SWTBfdW6#4db91c6c-d0b1-485d-a5c7-3d9bec7ff1df

#autentifikační číslo:
#https://support.uplisting.io/docs/api


# Note: If the endpoint does not respond to 5 different events in a row, our system will mark it as deactivated. From this point on, no further events will be posted to this endpoint until further notice.

# ----Webhooks can come in not sorted time line--------
# To resolve order issues, we recommend using the provided timestamp attribute, which represents the event's timestamp in UTC timezone and ISO8601 format.
# You should discard all webhooks with an earlier timestamp to prevent writing outdated data.

from flask import Flask, request, jsonify

import os
from pathlib import Path

import sys
from pathlib import Path

project_folder = Path(__file__).parent.parent.resolve()
sys.path.append(os.path.abspath(f"{project_folder}/")) 

from translate.pk_translate import *

from db import *
from identification_routes import *
from form_routes import *
from log_to_file import log_to_file
import ast
from load_config_ini import load_config_ini




################################

app = Flask(__name__)
app.secret_key = 'tv$$$ůj_ta%%323jný_klíč'  # Nutné pro flash zprávy

################################
# Registrace routs
register_identification_routes(app)
register_form_routes(app)

#log_to_file(str(app.url_map))

################################
# Receive webhook
@app.route('/webhooks', methods=['POST'])
def webhook():
    log_to_file(f"webhook received")
    try:
        if request.method == 'POST':
            
            received_data = request.json
           
            # if received_data.get('test') != 'test':
            #     log_to_file(f'webhook - webhook received: {received_data=}')
            #     webhook_id = received_data.get('id')
            #     log_to_file(f'webhook - {webhook_id=} - data are not stored in DB because testing mode')
            #     return jsonify({'message': 'ok'}), 200

            webhook_id = received_data.get('id')
            log_to_file(f'webhook - {webhook_id=} - {received_data=}')
            
            #Control of received data:
            # valid webhook must contain the following keys 
            keys_to_check = ['id', 'timestamp', 'guest_phone', 'number_of_guests', 'number_of_nights', 'check_in', 'check_out', 'guest_name', 'property_name']
            
            for key in keys_to_check:
                if received_data.get(key) == None or received_data.get(key) == "":
                    #webhook is not valid
                    
                    log_to_file(f'webhook -{webhook_id=} -  Webhook is not valid - missing key= ' + key)
                    
                    return jsonify({'message': 'Webhook is not valid'}), 500
                    #--end----------------

            # OK, webhook is valid
            # Load configuration from config.ini file
            number_of_attempts, checked_interval, blocked_interval, use_for_apartments = load_config_ini()


            # # to allow to use this app just for some apartments, in config.ini file must be set use_for_apartments=1,2,3,4,5. If value is ["all"] >>> all apartments are allowed
            if use_for_apartments == ['all']:
                pass
            elif str(received_data['property_name']).strip() not in use_for_apartments:
                log_to_file(f'webhook -{webhook_id=} -  Property name is not Allowed in Config.ini parameter >>> use_for_apartments - {received_data}')
              
                return jsonify({'message': 'Webhook is not valid'}), 200
                #--end----------------

            received_data['apartment_name'] = load_apartment_name(received_data['property_name'])
            apartment_name = received_data['apartment_name']
            log_to_file(f'webhook - {webhook_id=} - {apartment_name=}')

            #add webhook to db
            log_to_file(f'webhook - {webhook_id=} - data stored to db')

            result = add_webhook_to_db(received_data)
            

            # reply to the webhook sender
            if result == True:
                log_to_file(f"webhook -{webhook_id=} -  Webhook saved successfully")
                return jsonify({'message': 'ok'}), 200
                #--end----------------

            else:
                log_to_file(f"webhook - {webhook_id=} - Webhook saving error")
                log_to_file(f'webhook - {webhook_id=} - {result=}')
                
                return jsonify({'message': 'error'}), 500
                #--end----------------
           


    except Exception as e:
        log_to_file(f"webhook - {webhook_id=} - exception during webhook receiving: {e}")
        
        return jsonify({'message': 'error'}), 500

###############################
def load_apartment_name(property_name):
    
    try:
        property_name = property_name.replace(" ", "")

        with open(f"{project_folder}/data/apartments_spec.json", mode='r', encoding='utf-8') as f:
            apartments_spec = ast.literal_eval(f.read())
            apartment_name = apartments_spec.get(int(property_name)).get('Popis_formulář')
            if apartment_name:
                return apartment_name
            else:
                return 'Apartmán'
    
    except Exception as e:
        log_to_file(f"load_apartment_name - exception: {e}")
        return 'Apartmán'   


################################
# TEST
@app.route('/test', methods=['GET'])
def home():
    #log_to_file("home")
    return "test ok"

            
###############################
if __name__ == '__main__':  
    app.run(debug=True)
    



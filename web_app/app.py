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



################################

app = Flask(__name__)
app.secret_key = 'tv$$$ůj_ta%%323jný_klíč'  # Nutné pro flash zprávy

################################
# Registrace routs
register_identification_routes(app)
register_form_routes(app)

log_to_file(str(app.url_map))

################################
# Receive webhook
@app.route('/webhooks', methods=['POST'])
def webhook():
    log_to_file("webhook received")
    try:
        if request.method == 'POST':
            
            received_data = request.json
           
            log_to_file(f'{received_data=}')
            #Test received data:
            # valid webhook must contain the following keys 
            keys_to_check = ['id', 'timestamp', 'guest_phone', 'number_of_guests', 'number_of_nights', 'check_in', 'check_out', 'guest_name']
            
            for key in keys_to_check:
                if received_data.get(key) == None or received_data.get(key) == "":
                    #webhook is not valid
                    
                    log_to_file('Webhook is not valid - missing key= ' + key)
                    
                    return jsonify({'message': 'Webhook is not valid'}), 500
                    #--end----------------

            received_data['property_name'] = load_apartment_name(received_data['property_name'])

            #add webhook to db
            result = add_webhook_to_db(received_data)
            

            # reply to the webhook sender
            if result == True:
                log_to_file("Webhook saved successfully")
                return jsonify({'message': 'ok'}), 200
                #--end----------------

            else:
                log_to_file("Webhook saving error")
                log_to_file(f'{result=}')
                
                return jsonify({'message': 'error'}), 500
                #--end----------------
            
            #send_last_link(received_data)


    except Exception as e:
        log_to_file(f"exception during webhook receiving: {e}")
        
        return jsonify({'message': 'error'}), 500

###############################
def load_apartment_name(property_name):
    
    property_name = property_name.replace(" ", "")

    with open(f"{project_folder}/data/nazvy_bytu.csv", mode='r', encoding='utf-8') as f:
        apartments = f.readlines()
        
        for row in apartments:
            row = row.split(";")
            if row[0] == property_name:
                return row[1].replace("\n", "")        
    return 'Apartmán'

################################
# TEST
@app.route('/test', methods=['GET'])
def home():
    #log_to_file("home")
    return "test ok"

            
###############################
if __name__ == '__main__':  
    #app.run(port=5000, debug=True)

    #app.run(port=433, debug=False)
    #app.run(port=80, debug=True)
    app.run(debug=True)
    #print("3")



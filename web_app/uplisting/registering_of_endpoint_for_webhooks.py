# If you run this script in your terminal, it will send a POST request to the Uplisting API to register a new webhook endpoint. The webhook will be triggered when a new booking is created. The target URL of the webhook is set to https://www.homevibes.cz/webhook. The script uses the requests library to send the request and the json library to format the data as JSON. The response from the API is printed to the console. Make sure to replace the authorization token with your own token before running the script.
# If post from this code is successful, you will receive status code 201  and some ID code.


import requests
import json

def load_api_key():
    with open("uplisting/uplisting_key.txt", "r", encoding='utf-8') as file:
        api_key = file.read().strip()
    return api_key

#########################################
# Registering of endpoint for webhooks in Uplisting API 
def registering_of_endpoint_for_webhooks():

    

    url = "https://connect.uplisting.io/hooks"
    headers = {
        "Content-Type": "application/json",
        "Authorization": str(load_api_key())       
    }

    data = {
        "target_url": "https://www.homevibes.cz/webhooks",
        "event": "booking_created"
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    print("Status code:", response.status_code)
    print("Response text:", response.text)


    # Last Output on 11.2.2025:
    # Status code: 201
    # Response text: {"id":85549}

#########################################
def convert_api_key_to_base64():
    def text_to_base64(input_text):
        # Convert the input text to bytes
        input_bytes = input_text.encode('utf-8')
        # Encode the bytes to base64
        base64_bytes = base64.b64encode(input_bytes)
        # Convert the base64 bytes back to string
        base64_string = base64_bytes.decode('utf-8')
        return base64_string

    
    input_text = input("Enter the text to convert to base64: ")
    base64_string = text_to_base64(input_text)
    print("Base64 string:", base64_string)

#########################################
def verify_api_key():

    url = "https://connect.uplisting.io/users/me"

    payload={}
    headers = {
    'Authorization': str(load_api_key()),
    'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)

#########################################

# get list of active endpoints
def get_list_of_active_endpoints():

    url = "https://connect.uplisting.io/hooks"

    payload={}
    headers = {
    'Authorization': str(load_api_key())
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    response = response.json()
    for i in response['data']:
        print(i)
        print("\n---------------------\n")
    
   
  
#########################################
def remove_endpoint():

    id="83814"

    url = f"https://connect.uplisting.io/hooks/{id}"

    payload = ""
    headers = {
    'Content-Type': 'application/json',
    'Authorization': str(load_api_key())
    }

    response = requests.request("DELETE", url, headers=headers, data=payload)

    print(response.text)


#########################################

if __name__ == '__main__':  
    #registering_of_endpoint_for_webhooks()
    #convert_api_key_to_base64()
    #verify_api_key()
    #remove_endpoint()
    get_list_of_active_endpoints()

import requests

#there is used service https://app.smsmanager.com/cs/ to send sms

def send_sms(number, msg):
    try:
        number = number.replace(' ', '')
        number = number.replace('-', '')
        number = number.replace('/', '')
        number = number.replace('(', '')
        number = number.replace(')', '')
        number = number.replace('.', '')
        number = number.replace(',', '')
        number = number.replace('+', '')
        number = number.lstrip('0')

        #load the API key
        with open('sms_api_key/sms_api_key.txt', 'r', encoding="utf-8") as file:
            api_key = file.read().replace('\n', '')

        url = 'https://http-api.smsmanager.cz/Send'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'apikey': str(api_key),
            'number': number,
            'message': msg,
            'type': 'utf',
            }

        # Send POST request
        response = requests.post(url, headers=headers, data=data)

        return "ok"
    
    except Exception as e:
        return e
    
###############################
if __name__ == '__main__':
	pass
#    response = send_sms('00 420 724-928(604)  ', 'https://pkopecky.pythonanywhere.com/identification/1', 'Kopecký', 'Apartment 1')

#    print(response.text)pip install requests
##############################
# Google cloud project - Gmail API created by
# https://www.youtube.com/watch?v=PKLG5pfs4nY
#
# Gmail login OAuth2 and send by
# https://www.youtube.com/watch?v=44ERDGa9Dr4& list=PL3JVwFmb_BnSHlyy3gItOar_Y8w45mbJx
##############################

#pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

from send_email.Google import Create_Service
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
#import logs.logs as logs


def send_email_gmail(predmet, msg, email):

    #gmail api login
    CLIENT_SECRET_FILE = 'google_keys/OAuth 2 Client ID-gmail.json'
    API_NAME = 'gmail'
    API_VERSION = 'v1'
    SCOPES = ['https://mail.google.com/']

    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    mimeMessage = MIMEMultipart()

    mimeMessage['to'] = email #'pet.kopecky@gmail.com'
    mimeMessage['subject'] = predmet
    #mimeMessage['priority'] = 'high'
    mimeMessage.attach(MIMEText(msg, 'html'))
    raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()

    while True:
        try:
            #send message
            message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()
            #logs.create_log("send email about error","ok" ,message)

            return "ok", message
        except:
            #logs.create_log("send email about error", "chyba", "Error sending email")
            #time.sleep(5)
            print(f"Error sending email - {time.strftime('%d-%m-%Y %H:%M:%S')}")
            return "chyba"



# # pouze test
# if __name__ == "__main__":
#     # send_email_error("chyba-Test", f"{time.strftime('%d-%m-%Y %H:%M:%S')} - autorizace do gsheet - opakovaně se nepovedlo prihlasit do google sheet \n")
#     # print("done")
#     r= send_email_gmail("Test", "Test", "p.kopecky@centrum.cz")
#     print(r)
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from pathlib import Path


#######################################################
def send_smtp_email(predmet, text, TO):

    FROM = "booking@homevibes.cz"
    
    this_folder = Path(__file__).parent.resolve() 
    password_path = os.path.join(this_folder, 'email_password', 'email_password.txt')

    with open(password_path, "r") as f:
        PASSWORD = f.read().replace('\n', '')
        
    # Create the container email message.
    msg = MIMEMultipart()
    msg['From'] = FROM
    msg['To'] = TO
    msg['Subject'] = predmet

    # Attach the message body
    msg.attach(MIMEText(text, 'html'))

    try:
        # Connect to the server
        server = smtplib.SMTP_SSL('server12.mediapartner.cz', 465)
        server.login(FROM, PASSWORD)
        server.sendmail(FROM, TO, msg.as_string())
        server.quit()
        return "ok"

    except Exception as e:
        return f"Failed to send email: {str(e)}"



#######################################################
# # pouze test

if __name__ == "__main__":
    

    r= send_smtp_email('predmet', 'text', "p.kopecky@centrum.cz")

    print(r)
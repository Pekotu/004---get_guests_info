import sqlite3
from pathlib import Path
import sys
import pytz
from datetime import datetime


project_folder = Path(__file__).parent.parent.resolve() #cesta k projektu končí ve složce "004 - PYTHONANYWHERE
sys.path.append(f"{project_folder}/")

############################################
def get_db_path():

    project_folder = Path(__file__).parent.parent.resolve()
    db_path = f"{project_folder}/data/app_data.db"

    return db_path


############################################
def add_send_info_to_owner_to_db(booking_id):
    if booking_id != None and booking_id != '':

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        cursor.execute(f'''
            UPDATE webhooks_tbl
            SET sent_info_to_owner_at = CURRENT_TIMESTAMP
            WHERE booking_id = {booking_id}
        ''')

        conn.commit()
        conn.close()




############################################
def select_records_not_sent_to_owner():
    
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM webhooks_tbl
        WHERE
            sent_info_to_owner_at IS NULL
    ''')
    records = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    
    records_list = []
    for record in records:
        dict_record = dict(zip(columns, record))
        records_list.append(dict_record)
    
    conn.close()

    return records_list


##################################################
##################################################
def add_send_message_to_db(booking_id, message_category, email_sms):
    if booking_id != None and booking_id != '':

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        column_name = f'{message_category}_send_{email_sms}_at'
        
        cursor.execute(f'''
            UPDATE webhooks_tbl
            SET {column_name} = CURRENT_TIMESTAMP
            WHERE booking_id = {booking_id}
        ''')

        conn.commit()
        conn.close()
############################################
def add_send_message_error_to_db(booking_id, message_category, email_sms ):
    if booking_id != None and booking_id != '':

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        column_name = f'{message_category}_send_{email_sms}_error_at'

        cursor.execute(f'''
            UPDATE webhooks_tbl
            SET {column_name} = CURRENT_TIMESTAMP
            WHERE booking_id = {booking_id}
        ''')

        column_name = f'{message_category}_send_{email_sms}_error_counter'
        cursor.execute(f'''
            UPDATE webhooks_tbl
            SET {column_name} = {column_name} + 1 WHERE booking_id = {booking_id}
        ''')

        conn.commit()
        conn.close()

############################################
def select_records_with_not_sent_message(message_category, email_sms):
    
    #set today date 
    now = datetime.now(pytz.timezone("Europe/Prague"))
    today = now.strftime("%Y-%m-%d")
    

    #date selection
    # if message_category == 'arrival' select only records with check_in = today
    # if message_category == 'departure' select only records with check_out = today
    # if message_category == 'booking' dont take care about date
    if message_category == 'arrival':
        date_of_sending = 'check_in'
    elif message_category == 'departure':
        date_of_sending = 'check_out'

    column_send_at = f'{message_category}_send_{email_sms}_at'
    column_send_error = f'{message_category}_send_{email_sms}_error_counter'
    
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    if message_category == 'arrival' or message_category == 'departure':
        cursor.execute(f'''
            SELECT * FROM webhooks_tbl
            WHERE {column_send_at} IS NULL AND
                {column_send_error} < 5 AND
                {date_of_sending} = '{today}'
        ''')
    else: #booking
        cursor.execute(f'''
            SELECT * FROM webhooks_tbl
            WHERE {column_send_at} IS NULL AND
                {column_send_error} < 5
        ''')


    records = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    
    records_list = []
    for record in records:
        dict_record = dict(zip(columns, record))
        records_list.append(dict_record)
    
    conn.close()

    return records_list

          
############################################
if __name__ == '__main__':
	pass
#     #all_webhooks = return_all_webhooks()
#     hooks =  select_hooks_with_not_sent_link()


# #    hooks = return_all_webhooks()
#     for hook in hooks:
#         print(hook[0]," - ",hook[1])




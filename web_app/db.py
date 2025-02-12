import sqlite3

from pathlib import Path
import time

import sys
import os



project_folder = Path(__file__).parent.parent.resolve() #cesta k projektu končí ve složce "004 - PYTHONANYWHERE

# Přidání cesty do sys.path

sys.path.append(str(project_folder))


from translate.pk_translate import *


def get_db_path():

    project_folder = Path(__file__).parent.parent.resolve()
    db_path = f"{project_folder}\\data\\app_data.db"
    return db_path
    

############################################

def create_table_webhooks_tbl():

    conn = sqlite3.connect(get_db_path())

    cursor = conn.cursor()


     # Smazání původní tabulky, pokud existuje

    cursor.execute('DROP TABLE IF EXISTS webhooks_tbl;')
    

    cursor.execute('''

        CREATE TABLE IF NOT EXISTS webhooks_tbl (

            id INTEGER PRIMARY KEY,

            booking_id INTEGER,

            webhook TEXT,

            timestamp TIMESTAMP,

            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            phone TEXT,

            email TEXT,

            language TEXT,

            link_send_email_at TIMESTAMP,

            link_send_sms_at TIMESTAMP,

            link_send_email_error_at TIMESTAMP,       

            link_send_sms_error_at TIMESTAMP,

            link_send_email_error_counter INTEGER DEFAULT 0,

            link_send_sms_error_counter INTEGER DEFAULT 0,       

            data_from_form TEXT,

            data_from_form_at TIMESTAMP,

            form_data TEXT
            )
    ''')

    conn.commit()

    conn.close()

############################################

def create_table_ip_addresses_tbl():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

     # Smazání původní tabulky, pokud existuje
    cursor.execute('DROP TABLE IF EXISTS ip_addresses_tbl;')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ip_addresses_tbl (
            id INTEGER PRIMARY KEY,
            ip TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
    ''')
    conn.commit()
    conn.close()

############################################
def test():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # Zkontroluj tabulku ip_addresses_tbl
    cursor.execute('PRAGMA table_info(ip_addresses_tbl);')
    columns = cursor.fetchall()
    print(columns)

    conn.close()



############################################

def create_table_blocked_ip_tbl():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

     # Smazání původní tabulky, pokud existuje
    cursor.execute('DROP TABLE IF EXISTS blocked_ip_addresses_tbl;')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blocked_ip_addresses_tbl (
            id INTEGER PRIMARY KEY,
            ip_address TEXT,
            blocked_till TIMESTAMP default CURRENT_TIMESTAMP
                    )
    ''')

    conn.commit()
    conn.close()

############################################

def add_ip_address_to_db(ip_address):

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('''
            INSERT INTO ip_addresses_tbl (ip)
            VALUES (?)
            ''', (ip_address,))

    conn.commit()
    conn.close()

############################################

#return count of attempts by IP address in the last time_period seconds

def get_count_of_attempts_by_ip(ip_address, time_period=5*60):
    

    conn = sqlite3.connect(get_db_path())

    cursor = conn.cursor()
    

    cursor.execute('''

            SELECT COUNT(*) FROM ip_addresses_tbl

            WHERE ip = ? AND timestamp > datetime('now', ? || ' seconds')

        ''', (ip_address, -time_period))
        

    count = cursor.fetchone()[0]
    

    conn.close()
    
    return count


############################################

def add_blocked_ip_to_db(ip_address, blocked_till=None):

    if blocked_till is None:

        blocked_till = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() + 20*60))
    

    conn = sqlite3.connect(get_db_path())

    cursor = conn.cursor()
    

    cursor.execute('''

        INSERT INTO blocked_ip_addresses_tbl (ip_address, blocked_till)

        VALUES (?, ?)

    ''', (ip_address, blocked_till))
        

    conn.commit()

    conn.close()

############################################

def is_ip_blocked(ip_address):

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('''
            SELECT COUNT(*) FROM blocked_ip_addresses_tbl
            WHERE ip_address = ? AND blocked_till > datetime('now')
        ''', (ip_address,))
        
    count = cursor.fetchone()[0]
    conn.close()
    if count > 0:
        return True
    else:
        return False


############################################

def get_blocked_ip():

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('''
            SELECT * FROM blocked_ip_addresses_tbl
            ''')
        
    blocked_ips = cursor.fetchall()
    conn.close()

    
    return blocked_ips

############################################

# Add new webhook to the database if is fresher than the curent one with the same ID or if there is no webhook with the same ID

def add_webhook_to_db(webhook):


    try:    
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
       
        ##########
        def insert_webhook(webhook):
            # insert webhook
            cursor.execute('''
                INSERT INTO webhooks_tbl(booking_id, webhook, timestamp, received_at, phone, email, language)
                VALUES(?,?,?,?,?,?,?)

            ''', (webhook.get('id'), str(webhook), webhook.get('timestamp'), str(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())), webhook.get('guest_phone'), webhook.get('guest_email'), select_language_by_phone_number(webhook.get("guest_phone")) ))
        ##########

        # if in db is the webhook with the same ID and with timestamp before timestamp in received webhook, delete the old webhook and save the new one else keep the old one

        cursor.execute('''
        SELECT  COUNT(*) FROM webhooks_tbl 
        WHERE booking_id = ? AND timestamp < ?
        ''', (webhook.get('id'), webhook.get('timestamp')))

        count = cursor.fetchone()[0]

        if count > 0:
            # if webhook is found, delete it
            cursor.execute('''
                DELETE FROM webhooks_tbl 
                WHERE booking_id = ? AND timestamp < ?
            ''', (webhook.get('id'), webhook.get('timestamp')))

            insert_webhook(webhook)

        elif count == 0:
            # if webhook is not found, insert it
            insert_webhook(webhook)

        conn.commit()
        conn.close()

        return True
   

    except Exception as e:
        return e 

############################################

def add_data_from_form_to_db(booking_id, data_from_form):

    if booking_id != None and booking_id != '':
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute(f'''
            UPDATE webhooks_tbl
            SET data_from_form_at = CURRENT_TIMESTAMP,
            data_from_form = ?
            WHERE booking_id = ?
        ''', (str(data_from_form), booking_id))
        
        conn.commit()
        conn.close()


############################################
def change_language_in_db(booking_id, language):
    
    if booking_id != None and booking_id != '':
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute(f'''
            UPDATE webhooks_tbl
            SET language = ?
            WHERE booking_id = ?
        ''', (language, booking_id))


        conn.commit()
        conn.close()



############################################

def get_record_from_db(booking_id):
    #return all records from db with the booking_id as dictionary with names of columns

    if booking_id != None and booking_id != '':
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()  

        cursor.execute(f'''
            SELECT * FROM webhooks_tbl WHERE booking_id = {booking_id}
        ''')
        
        record = cursor.fetchone()
        columns = [column[0] for column in cursor.description]
        conn.close()
        if record == None:
            return None
        else:
            record_dic = dict(zip(columns, record))
            return record_dic

    
############################################

def get_all_records():

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM webhooks_tbl
    ''')
    
    records = cursor.fetchall()
    records_list = []
    columns = [column[0] for column in cursor.description]
    for row in records:
        records_list.append(dict(zip(columns, row)))
    
    conn.close()
    
    return records

############################################

def get_all_table_names():

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    conn.close()
    
    [print(table[0]) for table in tables]
    return tables

############################################

def delete_all_webhooks_from_db():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM webhooks_tbl
    ''')
    
    conn.commit()
    conn.close()



############################################

# Test whether link was sent to email 

def was_send_link_to_email(email, booking_id):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT link_send_email_at FROM webhooks_tbl 
        WHERE email = ? AND booking_id = ? AND link_send_email_at IS NOT NULL
    ''', (email, booking_id))
 

    records = cursor.fetchall()
    
    conn.close()
    
    if len(records) > 0:
        return True
    else:
        return False

############################################

# Test whether link was sent to phone 

def was_send_link_to_phone(phone, booking_id):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT link_send_sms_at FROM webhooks_tbl 
        WHERE phone = ? AND booking_id = ? AND link_send_sms_at IS NOT NULL
    ''', (phone, booking_id))

    records = cursor.fetchall()
    conn.close()

    if len(records) > 0:
        return True
    else:
        return False

############################################
def get_all_records_from_ip_tbl():

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM ip_addresses_tbl
    ''')
    

    records = cursor.fetchall()
    records_list = []
    columns = [column[0] for column in cursor.description]
    for row in records:
        records_list.append(dict(zip(columns, row)))
    

    conn.close()
    return records_list
    

############################################

if __name__ == '__main__':

    #create_table_webhooks_tbl()
    #create_table_ip_addresses_tbl()
    create_table_blocked_ip_tbl()

    #delete_all_webhooks_from_db()

    #get_all_table_names()
    
    # create_db()


    # i = 2000


    # hook = {'id': i, 'accommodation_management_fee': 20.0, 'accommodation_total': 362.45, 'arrival_time': '15:00:00', 'automated_messages_enabled': True, 'automated_reviews_enabled': False, 'booked_at': '2021-11-26T11:19:59Z', 'channel': 'airbnb_official', 'check_in': '2021-12-03', 'check_out': '2021-12-05', 'cleaning_fee': 40.0, 'cleaning_management_fee': 4.0, 'commission': 14.0, 'currency': 'GBP', 'departure_time': '11:00:00', 'direct': False, 'external_reservation_id': 'ABC2DEF3YZ', 'guest_email': 'kopeckysolution@seznam.cz', 'guest_name': 'Jon Snow', 'guest_phone': '+420724928604', 'manually_moved': False, 'multi_unit_id': None, 'multi_unit_name': None, 'note': 'Bringing the dragon', 'number_of_guests': 3, 'number_of_nights': 7, 'other_charges': None, 'preferred_guest_name': 'King of the North', 'property_id': 2, 'property_name': 'Mi Casa', 'source': None, 'status': 'confirmed', 'timestamp': '2021-11-26T11:20:00Z', 'total_management_fee': 48, 'total_payout': 388, 'webhook_received_at': '2024-11-18 18:35:20', 'my_status': 'received'}


    # for i in range(2000, 2007):

    #     hook['id'] = i

    #     add_webhook_to_db(hook)
    

    # all_webhooks = return_all_webhooks()

    # print("\n")

    # print(all_webhooks)

    # print("\n")



    # add_send_link_email_to_db(2003)

    # add_send_link_email_to_db(2005)

    # add_send_link_email_to_db(2006)


    # all_webhooks = get_all_records()

    # hooks = get_all_webhooks()

    # for hook in hooks:

    #     print(hook['booking_id'])

    #     print(hook['link_send_email_at'])

    #     print(hook['link_send_sms_at'])

    #     print(hook['webhook'])

    #     print("\n")

    #     print("----------------------")

    r = get_record_from_db(2)
    print(r.get('language'))

    change_language_in_db(2, "EN-GB")

    r = get_record_from_db(2)
    print(r.get('language'))
    
    
    #create_table_ip_addresses_tbl()
    #create_table_blocked_ip_tbl()
    #test()
    # a = get_blocked_ip()
    # print(a)

    

    
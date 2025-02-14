import sqlite3
from pathlib import Path
import sys


project_folder = Path(__file__).parent.parent.resolve() #cesta k projektu končí ve složce "004 - PYTHONANYWHERE
sys.path.append(f"{project_folder}/")


# def get_db_path():
#     project_folder = Path(__file__).parent.parent.resolve()
#     db_path = f"{project_folder}\\data\\app_data.db"
#     return db_path

def get_db_path():

    project_folder = Path(__file__).parent.parent.resolve()
    db_path = f"{project_folder}/data/app_data.db"

    #log_to_file(f"db_path: {db_path}")


    #--conn = sqlite3.connect(db_path)
    # cursor = conn.cursor()
    # cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    # tables = cursor.fetchall()

    # conn.close()

    # log_to_file(f"tables: {tables}")---------
    #

    return db_path

############################################
def add_send_link_email_to_db(booking_id):
    if booking_id != None and booking_id != '':

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        cursor.execute(f'''
            UPDATE webhooks_tbl
            SET link_send_email_at = CURRENT_TIMESTAMP
            WHERE booking_id = {booking_id}
        ''')

        conn.commit()
        conn.close()


############################################
def add_send_link_sms_to_db(booking_id):
    if booking_id != None and booking_id != '':

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        cursor.execute(f'''
            UPDATE webhooks_tbl
            SET link_send_sms_at = CURRENT_TIMESTAMP
            WHERE booking_id = {booking_id}
        ''')

        conn.commit()
        conn.close()

############################################
def add_send_link_email_error_to_db(booking_id):
    if booking_id != None and booking_id != '':

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        cursor.execute(f'''
            UPDATE webhooks_tbl
            SET link_send_email_error_at = CURRENT_TIMESTAMP
            WHERE booking_id = {booking_id}
        ''')

        cursor.execute(f'''
            UPDATE webhooks_tbl
            SET link_send_email_error_counter = link_send_email_error_counter + 1 WHERE booking_id = {booking_id}
        ''')

        conn.commit()
        conn.close()


############################################
def add_send_link_sms_error_to_db(booking_id):
    if booking_id != None and booking_id != '':

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        cursor.execute(f'''
            UPDATE webhooks_tbl
            SET link_send_sms_error_at = CURRENT_TIMESTAMP
            WHERE booking_id = {booking_id}
        ''')

        cursor.execute(f'''
            UPDATE webhooks_tbl
            SET link_send_sms_error_counter = link_send_sms_error_counter + 1 WHERE booking_id = {booking_id}
        ''')

        conn.commit()
        conn.close()





############################################
# return list of webhooks/records for with were not sent link
def select_hooks_with_not_sent_link():

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, booking_id, webhook, phone, email, language, link_send_email_at, link_send_sms_at  FROM webhooks_tbl
        WHERE
            link_send_email_at IS NULL AND
            link_send_sms_at IS NULL

    ''')

    webhooks = cursor.fetchall()
    webhooks_list = [
        {
            'id': webhook[0],
            'booking_id': webhook[1],
            'webhook': webhook[2],
            'phone': webhook[3],
            'email': webhook[4],
            'language': webhook[5],
            'link_send_email_at': webhook[6],
            'link_send_sms_at': webhook[7]
        }
        for webhook in webhooks
    ]

    conn.close()

    return webhooks_list


############################################
if __name__ == '__main__':
	pass
#     #all_webhooks = return_all_webhooks()
#     hooks =  select_hooks_with_not_sent_link()


# #    hooks = return_all_webhooks()
#     for hook in hooks:
#         print(hook[0]," - ",hook[1])




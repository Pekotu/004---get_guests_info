import pygsheets
#import pandas as pd
import time
import os
from pathlib import Path
import sys
import ast


project_folder = Path(__file__).parent.parent.resolve()
sys.path.append(os.path.abspath(f"{project_folder}/")) 

from log_to_file import log_to_file


############################
def login_to_google_sheets():
    #authorization
    error_counter = 0
    # Získání cesty k aktuálně běžícímu skriptu
    script_path = os.path.abspath(__file__)
    folder_path = Path(__file__).parent.resolve()

    log_to_file('login_to_google_sheets')

    while True:
        gc = pygsheets.authorize(service_file=f'{folder_path}/google_keys/get-guest-info-13d629337977.json')
        
        # 3x pokus o autorizaci poté výjimka
        if not gc:
            error_counter += 1

            if error_counter == 3:
                log_to_file("google_auth - Authorization failed")
                time.sleep(60)
                continue
                #raise Exception("Authorization failed")
            else:
                time.sleep(5)
                continue
        else:
            break
    return gc

############################
def write_data_to_gsheet(data_from_form, errors):
    try:
        #pokud je data_from_form string, převede je na slovník
        if type(data_from_form) == str:
            data_from_form = ast.literal_eval(data_from_form)

        ######## main ###########
        gc = login_to_google_sheets()
        start_time = time.time()
        

        # #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
        
        # Expect Google sheet with name Kniha_hostu_Home_Vibes where are sheets 'kniha' and 'errors'. 
        
        # list "kniha" has columns: id, form_data_stored_at, counter_of_saving, apartman, check_in, check_out, channel, booked_at, booked_by, booked_by_phone, booked_by_email
        
        # list "errors" has columns: id, first_name, family_name, birthday, street, town, country, passport, check_in, check_out, phone, email, error_first_name, error_family_name, error_birthday, error_street, error_town, error_country, error_passport, error_check_in, error_check_out, error_phone, error_email
        
        #file_name= "kniha_hostu" #'Kniha_hostu_Home_Vibes'
        file_id = '1f64-rTRXom85po9vlLAnfWaG0I1fSAYqX3WCZJ8kLH0'
        
        try:
            #sh = gc.open(file_name)
            sh = gc.open_by_key(file_id)
        except Exception as e:
            log_to_file(f"error - open_gsheet {file_name} - {e}")
            return str(e)

    ###################

        # Výběr listu "kniha"
        list = sh.worksheet_by_title('kniha')

        #reset filtru
        try:
            list.clear_basic_filter()
        except:
            pass

        # Načtení všech dat ze sloupce 'id'
        id_column = list.get_col(1, include_tailing_empty=False)

        headers = list.get_row(1, include_tailing_empty=False)
        data_list = [''] * len(headers)

        id = data_from_form.get('id')
        t1_mazani = time.time()
        #mazaní řádků se shodným ID
        if id != None:
            rows_to_delete = []
            # hledání booking id ve sloupci 'id' a vybere řádek které obsahují ID
            for i, value in enumerate(id_column):
                if value == id:  # Pokud je hodnota shodná s ID
                    rows_to_delete.append(i + 1)  # Přidáme číslo řádku (indexování od 1)

            # Odstraňujeme řádky s hodnotou id v prvním sloupci
            for row in reversed(rows_to_delete):  # Procházet zpětně, abychom neovlivnili indexy při mazání
                list.delete_rows(row)
            
            t2_mazani = time.time()

            # zapíše data z formuláře do tabulky
            # kde každý host je jeden řádek
            l=len(id_column) 
            print(f"{len(id_column)=}")

            id_column = list.get_col(1, include_tailing_empty=False)
            row = len(id_column) + 1
            host=0
            
            #gsheet neumí zapsat + na začátek telefonního čísla   
            if data_from_form.get('booked_by_phone'):
                data_from_form.get('booked_by_phone').replace('+','')

            while data_from_form.get('first_name_' + str(host)) != None: 
                values = []
                for sl, header in enumerate(headers):
                    if header in ['id', 'form_data_stored_at', 'counter_of_saving', 'apartman', 'check_in', 'check_out', 'channel', 'booked_at', 'booked_by', 'booked_by_phone', 'booked_by_email']:
                        key = header
                    else:
                        key = header + '_' + str(host)

                    values.append(data_from_form.get(key,'-'))
                    #list.update_value((row,sl+1), data_from_form.get(key,'-'))
                
                list.update_row(row, values)

                host += 1
                row += 1
            t3_zapis = time.time()
            print(f"mazani: {t2_mazani-t1_mazani} zapis: {t3_zapis-t2_mazani}")

            #nastaví filtr na všechny řádky s daty 
            list.set_basic_filter(start=(1,1), end=(row-1,len(headers)))

            #zapíše chyby při vyplnování formuláře
            write_errors_from_form_to_gsheet(id, sh, errors)

        return "ok"

    except Exception as e:
        log_to_file(f"error - write_data_to_gsheet - id:{data_from_form.get('id')} - {e}")
        return str(e)

############################
#zapíše počty chyb při vyplňování formuláře do listu 'errors'
def write_errors_from_form_to_gsheet(id, sh, errors):
    #errors = load_errors_from_form(id)
    errors['id'] = id
    # Výběr listu "kniha"
    list = sh.worksheet_by_title('errors')

    #reset filtru
    try:
        list.clear_basic_filter()
    except:
        pass

    # Načtení všech dat ze sloupce 'id'
    id_column = list.get_col(1, include_tailing_empty=False)

    headers = list.get_row(1, include_tailing_empty=False)
    

    #mazaní řádků se shodným ID
    if id != None:
        rows_to_delete = []
        # hledání booking id ve sloupci 'id' a vybere řádek které obsahují ID
        for i, value in enumerate(id_column):
            if value == id:  # Pokud je hodnota shodná s ID
                rows_to_delete.append(i + 1)  # Přidáme číslo řádku (indexování od 1)

        # Odstraňujeme řádky s hodnotou id v prvním sloupci
        for row in reversed(rows_to_delete):  # Procházet zpětně, abychom neovlivnili indexy při mazání
            list.delete_rows(row)
 
        # zapíše data z errors do tabulky
    
        id_column = list.get_col(1, include_tailing_empty=False)
        row = len(id_column) + 1
           
        
        values = []
        for sl, header in enumerate(headers):
            values.append(errors.get(header,'0'))
            
        list.update_row(row, values)

        #nastaví filtr na všechny řádky s daty 
        list.set_basic_filter(start=(1,1), end=(row,len(headers)))
    return
    

############################
if __name__ == '__main__':
    #x= login_to_google_sheets()

    gc = login_to_google_sheets()
    
    
    file_name='Kniha_hostu_Home_Vibes'
    try:
        sh = gc.open(file_name)
         # Výběr listu "kniha"
        list = sh.worksheet_by_title('kniha')

        print(list)
    except Exception as e:
        log_to_file(f"error - open_gsheet {file_name} - {e}")
        

    ###################

       
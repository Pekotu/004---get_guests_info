import os
import pathlib
import sys
from log_to_file import log_to_file

project_folder = pathlib.Path(__file__).parent.parent.resolve()

path_store_data_to_googlesheet = (os.path.abspath(f"{project_folder}/web_app/store_data_to_googlesheet/") )
sys.path.append(path_store_data_to_googlesheet)
from direct_connection_to_gsheet import login_to_google_sheets

# load specification of apartments from Google Sheets
# data will be stored in dictionary apartments_spec where key is 'Číslo' = number of apartment

# Connect to Google Sheets
def load_apartments_spec():
    gc = login_to_google_sheets()

    #file - 'Názvy bytů'
    file_id = '1f64-rTRXom85po9vlLAnfWaG0I1fSAYqX3WCZJ8kLH0'
    

    try:
        sh = gc.open_by_key(file_id)
    except Exception as e:
        log_to_file(f"error - open_gsheet {file_id} - {e}")
        #return str(e)

    # Get list of all files in Google Sheets

    sh = gc.open_by_key(file_id)

    # Výběr listu "kniha"
    list = sh.worksheet_by_title('seznam_apartmanu')
    #reset filtru
    try:
        list.clear_basic_filter()
    except:
        pass

    # Read all non-empty rows from the sheet
    rows = list.get_all_records(empty_value = '', head = 1, majdim = 'ROWS', numericise_data = True)    

    apartments_spec = {row['Číslo']: row  for row in rows}

    #obecne_info = apartments_spec[52]['Popis_formulář']

    #store to folder data to be used in web_app
    with open(f"{project_folder}/data/apartments_spec.json", 'w', encoding='utf-8') as f:
        f.write(str(apartments_spec))

    return apartments_spec  


if __name__ == '__main__':
    pass
    #load_apartments_spec()
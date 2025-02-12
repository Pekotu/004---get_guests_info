import os
import json
import deepl #$ pip3 install deepl
from datetime import datetime
import time
import locale
from pathlib import Path
import sys


project_folder = Path(__file__).parent.parent.resolve()
sys.path.append(os.path.abspath(f"{project_folder}/"))
from web_app.log_to_file import log_to_file




phone_international_codes_path='' # cesta k souboru s mezinárodnímu předvolbami telefonních čísel
content_folder_path='' # cesta k adresáři s texty pro překlad

###############################
# get DATA folders paths
def get_data_paths():

    global phone_international_codes_path # path to file with international phone codes
    global content_folder_path # path to folder with texts for translation

    # Get the path to the currently running script
    script_path = os.path.abspath(__file__)
    # Get the path to the directory where the script is located
    slozka_skriptu = os.path.dirname(script_path)
    # Get the path to the parent directory
    nadrazena_slozka = os.path.dirname(slozka_skriptu)
    
    phone_international_codes_path = os.path.join(slozka_skriptu,"phone_international_codes", 'International_phone_codes_languages.csv') # path to file with international phone codes
    
    content_folder_path = os.path.join(slozka_skriptu,"content") # path to folder with texts for translation
    return

###############################

def select_language_by_phone_number(phone_number):
    
    get_data_paths()
    
    phone_number = phone_number.replace(' ', '')
    phone_number = phone_number.replace('+', '')
    phone_number = phone_number.replace('.', '')
    phone_number = phone_number.replace(',', '')
    phone_number = phone_number.replace('(', '')
    phone_number = phone_number.replace(')', '')
    phone_number = phone_number.replace('/', '')
    phone_number = phone_number.replace('\\', '')
    phone_number = phone_number.replace(';', '')
    phone_number = phone_number.replace(':', '')
    phone_number = phone_number.replace('!', '')

    with open(phone_international_codes_path, mode='r', encoding='utf-8') as f:
        
        phone_codes_language = f.readlines() #return list of strings
        
        for row in phone_codes_language:
            row = row.replace('\n', '')
            row  = row.split(";")
            
            if phone_number.startswith(row[1]):
                print(row)
                print(phone_number)
                return row[4].upper()
        # if phone number is not in the list, return default language
    print(phone_number)
    return 'CS'
    
###############################
def translate_content(content_name, webhook, language = 'CS' ):
    
    get_data_paths()

        
    # Check if the file with target language already exists just use it, if not, open default language file and translate text to target language
    language_file_path = f"{content_folder_path}/{language}_{content_name}.json".lower()
    
    #if file with target language exists, use it
    if os.path.exists(language_file_path):
        with open(language_file_path, mode='r', encoding='utf-8') as f:
            content = json.load(f)
            need_translate = False
            
    
    else: #if file with target language does not exist, open default language file and translate text to target language
        with open(f"{content_folder_path}/cs_{content_name}.json", mode='r', encoding='utf-8') as f:
            content = json.load(f)
            need_translate = True

    if language != 'CS' and need_translate == True:
        
        # authentication key for DeepL
        with open("translate_api_key/deepl_api_ket.txt", mode='r', encoding='utf-8') as f:
            auth_key = f.read().replace('\n', '')

        # three attempts to connect with DeepL
        for i in range(3):
            try:
                translator = deepl.Translator(auth_key)
                break
            except Exception as e:
                log_to_file(f"Failed to connect to DeepL: {str(e)}")
                
                time.sleep(0.5)
                if i == 2:
                    log_to_file("Failed to connect to DeepL: {str(e)})")
                    return content #return original text if failed to create translator
                continue
        

        #if connection was successful, translate text
        #translate all keys in content
        translate_error = 0
        for key in content:
            if translate_error > 3: #if failed to translate 3 times, return original text
                log_to_file("3times Failed translation of content[key]: {key} in {content_name=}")
                break
            
            else: #try to translate text 3 times
                for i in range(3):
                    try:

                        content[key] = translator.translate_text(
                            content[key], 
                            source_lang = "CS", 
                            target_lang = language, 
                            model_type = "prefer_quality_optimized").text
                        break
                    except Exception as e:
                        log_to_file(f"Failed to translate text: {str(e)}")
                        time.sleep(0.5)
                        
                        if i == 2:
                            log_to_file("Failed to translate text")
                            translate_error += 1    
                        continue

    #remove <keep> tags from content
    for key in content:
        content[key] = content[key].replace("<keep>", "")
        content[key] = content[key].replace("</keep>", "")
    
    #save translated content to file
    if language != 'CS' and need_translate == True:
        with open(f"{content_folder_path}/{language.lower()}_{content_name}.json", mode='w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        
    return content #return translated text


###############################

# if __name__ == "__main__":
#     get_data_paths()
#     content_name = 'email'
#     phone_number = '+1 777 123 456'
#     webhook = {
#         'language': "EN-GB",
#         'property_name': '2', 'check_in': '2024-11-24', 'check_out': '2024-11-25'}
#     result = translate_content(content_name, webhook, language = 'CS')
#     for key in result:
#         print(key,"=", result[key])
        
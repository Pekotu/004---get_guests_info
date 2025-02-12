--------CZ--------------------
Vytvořil: Petr Kopecký
petr@kopeckysolution.com
12.2.2025

Aplikace má 3 hlavní funkce.

1) 
Flask aplikace. Uloženo ve složce "web_app", hlavní soubor je app.py. Komunikaci mezi apache serverem a aplikací je řízená přes Gunicorn. Konfigurační soubor Gunicornu je uložený ve složce web_app/gunicorn_config.py

Aplikace zajišťuje příjem webhooků z externí služby uplisting.io. Webhooky obsahují informace o rezervacích ubytovacích kapacit.
Data přijatá pomocí webhooků jsou ukládána do databáze, použita je SQLite.
Při ukládání dat to databáze je definovaný jazyk pro komunikaci se zákazníkem. Jazyk je určen podle mezinárodní telefonní předvolby. 
Přijatá data jsou před uložením otestovaná, zda obsahují všechna důležité informace a nejedená se o podvrh.
Nakonec aplikace vrací serverů odpověď zda data přijal nebo ne 200 nebo 500.
Aby služba uplisting posílala webhooky na adresu kde tato aplikace poslouchá, je zapotřebí jí nastavit. V dokumentaci je uvedeno jak se to dělá. Ve složce web_app/uplisting/registering_of_endpoint_for_webhooks.py je skript, který byl použit pro nastartování odesílání webhooku. 
Uplisting má pravidlo, že pokud nedostane kladnou odpověď "200" na 20 po sobě jdoucích webhooků, tak ukončí jejich posílání na danou url.  

2)
Send_link.py  je ve složce send_link.
Jedná se o samostatný proces, který v nastaveném intervalu 30 sekund, kontroluje nově příchozí webhooky v databázi. A na telefonní čísla a emaily uložené v těchto datech odesílá odkaz přes který se zákazník/uživatel dostane na webovou stránku, kde bude vyzván k zadání informací o ubytovaných osobách ( online check-in ). Zpráva je v jazyce odpovídající mezinárodní telefonní předvolbě.
K odesílání SMS je používaná externí služba. Email je odesílaný přes SMTP server.

3)
Třetím procesem je generování webových stránek pro zadávání údajů o hostech a následné zpracování a uložení informací zapsaných do formulářů. Stránky jsou generované stejnou flask aplikací jako v procesu 1.
První stránka na kterou se zákazník dostane provádí identifikaci uživatele, kde je vyzván k zadání emailu nebo telefonního čísla na které dostal odkaz přes který se dostal na tuto stránku. Smyslem této stránky je zamezit přístup uživatelům kteří zde nemají co dělat. Při opakovaném zadání špatného tel čísla nebo emailu je ip zablokovaná na 20min.
Po úspěšné identifikaci je uživatel přesměrován na druhou stránku, kde je dynamicky vytvořený formulář pro zadání základních kontaktních informací o hostech, kteří budou ubytovaní v rezervovaný termín. Pokud již dříve do formuláře uživatel uložil nějaká data, tak při opětovné návštěvě se data načtou.
Při odesílání dat jsou hodnoty kontrolované, tak aby byly alespoň trochu blízké pravdě, tudíž datum narození, adresa, číslo občanky, nebo jméno musí mít požadovanou délku a obsahovat jen povolené znaky. Pokud některý z parametrů není splněný, tak se formulář uživateli objeví znova s výzvou aby ji opravil.
Když jsou zadaná data správná, tak jsou uložená do databáze a současně se ukládají do Google sheet tabulky. Zde jsou také ukládané statistiky o chybách které uživatel udělal při vyplňování formuláře. 
Tento proces potřebuje mít kontrolu že je zapnutý. Tudíž je zapotřebí na serveru vytvořit unit file, který bude proces startovat, pokud bude ukončen nebo server bude restartován.

Překládání textu je řešeno pomocí api DeepL. Aby byl šetřen čas a výkon, tak jakmile je jednou text do jazyka přeložený, tak se výsledek uloží. A v budoucnu když bude jazyk potřeba znovu, tak už se nebude překládat a použije se dříve uložený text. Toto je zapotřebí brát v potaz v momentě, kdy se budou hlavní texty, které jsou v češtině, měnit. V ten okamžik je zapotřebí smazat všechny dříve přeložené texty, aby došlo k opětovnému přeložení. Pro překládání je využívám free účet DeepL který může přeložit 500 000 znaků za měsíc.

Nasazení aplikace:
Kroky které je zapotřebí provést při nasazení aplikace na linux server s apache je popsán v souboru application_launch_procedure.txt



--------EN--------------------
Created by: Petr Kopecký
petr@kopeckysolution.com
12.Feb.2025

The application has 3 main functions.

1)
Flask application. Stored in the "web_app" folder, the main file is app.py. Communication between the apache server and the application is controlled via Gunicorn. The Gunicorn configuration file is stored in the web_app/gunicorn_config.py folder

The application ensures the reception of webhooks from the external service uplisting.io. Webhooks contain information about accommodation reservations.
Data received using webhooks is stored in a database, SQLite is used.
When storing data, the database is the defined language for communication with the customer. The language is determined by the international telephone prefix.
Received data is tested before being stored to ensure that it contains all important information and is not a fake.
Finally, the application returns a response from the server indicating whether the data was received or not, 200 or 500.
In order for the uplisting service to send webhooks to the address where this application is listening, it needs to be configured. The documentation explains how to do this. In the web_app/uplisting/registering_of_endpoint_for_webhooks.py folder, there is a script that was used to start sending webhooks.
Uplisting has a rule that if it does not receive a positive response of "200" for 20 consecutive webhooks, it stops sending them to the given url.

2)
Send_link.py is in the send_link folder.
This is a separate process that checks the database for newly arriving webhooks at a set interval of 30 seconds. And to the phone numbers and emails stored in this data, it sends a link through which the customer/user will get to a website, where he will be asked to enter information about the accommodated persons (online check-in). The message is in the language corresponding to the international telephone code.
An external service is used to send SMS. Email is sent via SMTP server.

3)
The third process is the generation of websites for entering guest data and subsequent processing and saving of information entered into forms. The pages are generated by the same flask application as in process 1.
The first page that the customer gets to identifies the user, where he is asked to enter the email or phone number to which he received the link through which he got to this page. The purpose of this page is to prevent access by users who have no business here. If you repeatedly enter a wrong phone number or email, the IP is blocked for 20 minutes.
After successful identification, the user is redirected to the second page, where there is a dynamically created form for entering basic contact information about the guests who will be accommodated on the reserved date. If the user has previously saved some data in the form, the data will be loaded when visiting again.
When sending data, the values ​​are checked so that they are at least somewhat close to the truth, so the date of birth, address, ID number, or name must have the required length and contain only permitted characters. If any of the parameters are not met, the form will appear again to the user with a prompt to correct it.
When the entered data is correct, it is saved to the database and at the same time saved to the Google sheet table. Statistics on errors made by the user when filling out the form are also stored here.
This process needs to be checked to ensure that it is turned on. Therefore, it is necessary to create a unit file on the server that will start the process if it is terminated or the server is restarted.

Text translation is solved using the DeepL API. To save time and performance, once a text is translated into a language, the result is saved. And in the future, when the language is needed again, it will not be translated and the previously saved text will be used. This needs to be taken into account when the main texts in Czech are changed. At that moment, all previously translated texts need to be deleted in order to be translated again. For translation, I use a free DeepL account that can translate 500,000 characters per month.

Application Deployment:
The steps required to deploy an application on a Linux server with Apache are described in the application_launch_procedure.txt file
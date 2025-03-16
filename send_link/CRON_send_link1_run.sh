#!/bin/bash

# Soubor pro logování
LOG_FILE="/var/www/clients/client1/web26/web/get_guest_info/send_link/cronlog1.log"

# Hledáme proces "send_link1" a zapisujeme výstup do logu
echo "--------------------" >> $LOG_FILE
echo "Kontrola procesů - $(date)" >> $LOG_FILE

echo "Hledání procesů send_link1: $(pgrep -af "send_link1")" >> $LOG_FILE

if ! pgrep -af "python.*send_link1" >> $LOG_FILE 2>&1
then
  # Pokud proces není spuštěn, spustíme ho a zapíšeme do logu
  echo "Proces 'send_link' není spuštěn, spouštím ho..." >> $LOG_FILE
  /var/www/clients/client1/web26/web/get_guest_info/send_link/venv/bin/python /var/www/clients/client1/web26/web/get_guest_info/send_link/send_link1.py & >> $LOG_FILE 2>&1
else
  # Pokud proces běží, vypíšeme do logu, že již běží
  echo "Proces 'send_link1' již běží." >> $LOG_FILE
fi

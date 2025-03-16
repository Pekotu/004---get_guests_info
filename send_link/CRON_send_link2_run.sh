#/var/www/clients/client1/web26/web/get_guest_info/send_link/

#!/bin/bash

# Hledáme proces "send_link2"
if ! pgrep -f "send_link2" > /dev/null
then
  # Pokud proces není spuštěn, spustíme ho
  echo "Proces 'send_link2' není spuštěn, spouštím ho..."
  /var/www/clients/client1/web26/web/get_guest_info/send_link/venv/bin/python /var/www/clients/client1/web26/web/get_guest_info/send_link/send_link2.py &
else
  # Pokud proces běží, vypíšeme, že už běží
  echo "Proces 'send_link2' již běží."
fi

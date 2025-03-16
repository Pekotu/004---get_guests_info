from send_email.send_smtp_email import send_smtp_email
import datetime

if __name__ ==  '__main__':
    try:
        with open('/var/www/clients/client1/web26/web/get_guest_info/send_link/test_cron.txt', 'a') as f:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f'START \n')
    except Exception as e:
        print(f'{e=}')

    try:
        send_smtp_email('test cron', f'Cron {now=} ', 'kopeckysolution@seznam.cz')

    except Exception as e:
        with open('test_cron.txt', 'a') as f:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f'{now} - Error: {e}\n')


    with open('test_cron.txt', 'a') as f:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f'konec - Cron job executed \n')

    print(f'Email sent {now}')
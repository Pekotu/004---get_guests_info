phone = "00420 777 777 777"

if phone[0:2]== "00": 
    phone  = f"+{phone[2:]}"

print(phone)            
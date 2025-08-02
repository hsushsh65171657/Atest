import requests
import time
from uuid import uuid4
tok=input(' Token Tele : ');iD=input(' ID Tele : ');user=input(' Username Instagram : ');pas=input(' Password Instagram : ')

def login():
    global user,pas
    ud = str(uuid4)
    user = user
    pas = pas
    url ='https://b.i.instagram.com/api/v1/accounts/login/'
    headers ={

        'Host': 'i.instagram.com',
        'X-Pigeon-Session-Id': '6509efe7-903a-473a-bc6c-c6e991b00863',
        'X-Pigeon-Rawclienttime': '1699804011.337',
        'X-Ig-Connection-Speed': '-1kbps',
        'X-Ig-Bandwidth-Speed-Kbps': '-1.000',
        'X-Ig-Bandwidth-Totalbytes-B': '0',
        'X-Ig-Bandwidth-Totaltime-Ms': '0',
        'X-Bloks-Version-Id': '009f03b18280bb343b0862d663f31ac80c5fb30dfae9e273e43c63f13a9f31c0',
        'X-Ig-Connection-Type': 'WIFI',
        'X-Ig-Capabilities': '3brTvw==',
        'X-Ig-App-Id': '567067343352427',
        'User-Agent': 'Instagram 100.0.0.17.129 Android (28/9; 300dpi; 900x1600; Asus; ASUS_I003DD; ASUS_I003DD; intel; en_US; 161478664)',
        'Accept-Language': 'en-US',
        'Cookie': 'mid=ZVDJJAABAAF1siKcQXtdWVMgki95; csrftoken=jCYC9fu0Gt2BQrZKe4iyfGH2BienwPy1',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept-Encoding': 'gzip, deflate, br',
        'X-Fb-Http-Engine': 'Liger',
        'Connection': 'keep-alive',
        'Content-Length': '757'

    }

    data ={
        #'igned_body':'dd22894d8f4affcfa28d020d64288ae739e4782efeed0fa303dbe5200080a593',
        "country_codes":"[{\"country_code\":\"1\",\"source\":[\"default\"]},{\"country_code\":\"964\",\"source\":[\"sim\"]}]",
        "phone_id":ud,
        "_csrftoken":"jCYC9fu0Gt2BQrZKe4iyfGH2BienwPy1",
        "username":f"{user}",
        "adid":ud,
        "guid":ud,
        "device_id":ud,
        "google_tokens":"[]",
        "password":f"{pas}",
        "login_attempt_count":"0",
        'ig_sig_key_version':'4'
    }

    re = requests.post(url,headers=headers,data=data)
    #print(re.text)
    if ('"bad_password"') in re.text:
        data5 = {'login':'password false','no':{'no':'Login'}}
        print(data5)
    elif ('"invalid_user"') in re.text:
        data4 = {'login':'no user','no':{'no':'Login'}}
        print(data4)
    elif ('"checkpoint_challenge_required"') in re.text:
        #"checkpoint_challenge_required"
        data2 = {'login':'secuer','no':{'no':'Login'}}
        print(data2)
    elif ('"Your account has been disabled for violating our terms. Learn how you may be able to restore your account."') in re.text:
        data3 = {'login':'band','no':{'no':'Login'}}
        print(data3)
    elif ('"two_factor_required"') in re.text:
        data9 = {'login':'verification','no':{'no':'Login'}}
        print(data9)

    elif ('"status":"ok"') in re.text:
        cok = re.cookies                
        ko = cok.get_dict()
        sessoin = ko['sessionid']
        print('[√] Sessionid : ',sessoin)
        L7N = sessoin
        requests.post(f"https://api.telegram.org/bot{tok}/sendMessage?chat_id={iD}&text="+str(L7N))
    
    else:
        data7 = {'login':'error'}
        print(data7)
login()

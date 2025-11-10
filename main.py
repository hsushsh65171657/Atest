import requests, uuid, string, random, re, base64, urllib.parse

my_uuid = uuid.uuid4()
my_uuid_str = str(my_uuid)
modified_uuid_str = my_uuid_str[:8] + "should_trigger_override_login_success_action" + my_uuid_str[8:]
rd = ''.join(random.choices(string.ascii_lowercase+string.digits, k=16))

def _extract_from_set_cookie(header, name):
    # يحاول يجيب قيمة كوكي من هيدر Set-Cookie
    if not header:
        return None
    m = re.search(rf"{re.escape(name)}=([^;,\s]+)", header)
    return m.group(1) if m else None

def login(user,password):
    data = {"params": "{\"client_input_params\":{\"contact_point\":\"" + user + "\",\"password\":\"#PWD_INSTAGRAM:0:0:" +  password + "\",\"fb_ig_device_id\":[],\"event_flow\":\"login_manual\",\"openid_tokens\":{},\"machine_id\":\"ZG93WAABAAEkJZWHLdW_Dm4nIE9C\",\"family_device_id\":\"\",\"accounts_list\":[],\"try_num\":1,\"login_attempt_count\":1,\"device_id\":\"android-" + rd + "\",\"auth_secure_device_id\":\"\",\"device_emails\":[],\"secure_family_device_id\":\"\",\"event_step\":\"home_page\"},\"server_params\":{\"is_platform_login\":0,\"qe_device_id\":\"\",\"family_device_id\":\"\",\"credential_type\":\"password\",\"waterfall_id\":\"" + modified_uuid_str + "\",\"username_text_input_id\":\"9cze54:46\",\"password_text_input_id\":\"9cze54:47\",\"offline_experiment_group\":\"caa_launch_ig4a_combined_60_percent\",\"INTERNAL__latency_qpl_instance_id\":56600226400306,\"INTERNAL_INFRA_THEME\":\"default\",\"device_id\":\"android-" + ''.join(random.choices(string.ascii_lowercase+string.digits, k=16)) + "\",\"server_login_source\":\"login\",\"login_source\":\"Login\",\"should_trigger_override_login_success_action\":0,\"ar_event_source\":\"login_home_page\",\"INTERNAL__latency_qpl_marker_id\":36707139}}"}
    data["params"] = data["params"].replace("\"family_device_id\":\"\"", "\"family_device_id\":\"" +my_uuid_str + "\"")
    data["params"] = data["params"].replace("\"qe_device_id\":\"\"", "\"qe_device_id\":\"" + my_uuid_str + "\"")
    headers = {"Host": "i.instagram.com","X-Ig-App-Locale": "ar_SA","X-Ig-Device-Locale": "ar_SA","X-Ig-Mapped-Locale": "ar_AR","X-Pigeon-Session-Id": f"UFS-{uuid.uuid4()}-0","X-Pigeon-Rawclienttime": "1685026670.130","X-Ig-Bandwidth-Speed-Kbps": "-1.000","X-Ig-Bandwidth-Totalbytes-B": "0","X-Ig-Bandwidth-Totaltime-Ms": "0","X-Bloks-Version-Id": "8ca96ca267e30c02cf90888d91eeff09627f0e3fd2bd9df472278c9a6c022cbb","X-Ig-Www-Claim": "0","X-Bloks-Is-Layout-Rtl": "true","X-Ig-Device-Id": f"{uuid.uuid4()}","X-Ig-Family-Device-Id": f"{uuid.uuid4()}","X-Ig-Android-Id": f"android-{''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}","X-Ig-Timezone-Offset": "10800","X-Fb-Connection-Type": "WIFI","X-Ig-Connection-Type": "WIFI","X-Ig-Capabilities": "3brTv10=","X-Ig-App-Id": "567067343352427","Priority": "u=3","User-Agent": f"Instagram 303.0.0.0.59 Android (28/9; 320dpi; 900x1600; {''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}/{''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}; {''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}; {''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}; {''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}; en_GB;)","Accept-Language": "ar-SA, en-US","Ig-Intended-User-Id": "0","Content-Type": "application/x-www-form-urlencoded; charset=UTF-8","Content-Length": "1957","Accept-Encoding": "gzip, deflate","X-Fb-Http-Engine": "Liger","X-Fb-Client-Ip": "True","X-Fb-Server-Cluster": "True"}
    response = requests.post('https://i.instagram.com/api/v1/bloks/apps/com.bloks.www.bloks.caa.login.async.send_login_request/',headers=headers ,data=data)
    body = response.text

    if "Bearer" in body:
        # استخراج الـ bearer -> تفكيك الـ base64 -> اخذ sessionid من الـ payload
        try:
            session_b64 = re.search(r'Bearer IGT:2:(.*?),', response.text).group(1).strip()
            session_b64 = session_b64[:-8]
            full = base64.b64decode(session_b64).decode('utf-8')
        except Exception as e:
            full = ""
        sessionid_from_full = None
        if "sessionid" in full:
            m = re.search(r'"sessionid":"(.*?)"', full)
            if m:
                sessionid_from_full = m.group(1).strip()

        # حاول تجيب الكوكيز من response.cookies أولاً
        cookies = response.cookies
        csrftoken = cookies.get('csrftoken') or _extract_from_set_cookie(response.headers.get('Set-Cookie',''), 'csrftoken')
        rur = cookies.get('rur') or _extract_from_set_cookie(response.headers.get('Set-Cookie',''), 'rur')
        mid = cookies.get('mid') or _extract_from_set_cookie(response.headers.get('Set-Cookie',''), 'mid')
        ds_user_id = cookies.get('ds_user_id') or _extract_from_set_cookie(response.headers.get('Set-Cookie',''), 'ds_user_id')
        sessionid_cookie = cookies.get('sessionid') or _extract_from_set_cookie(response.headers.get('Set-Cookie',''), 'sessionid')

        # إذا لقينا sessionid من الـ payload (decoded) نستخدمه، وإلا نستخدم اللي من الكوكيز
        final_sessionid = sessionid_from_full or sessionid_cookie

        # بعض الـ sessionid يكون مشفّر مسبقاً (مثلاً يحتوي %3A)، فإذا تريد تشفيره:
        # final_sessionid_quoted = urllib.parse.quote(final_sessionid, safe='') if final_sessionid else None
        # بناء سترينغ الكوكيز بالشكل المطلوب - نحتفظ بالقيم اللي لقيناها فقط
        cookie_items = []
        if csrftoken:
            cookie_items.append(f"csrftoken={csrftoken}")
        if rur:
            cookie_items.append(f"rur={rur}")
        if mid:
            cookie_items.append(f"mid={mid}")
        if ds_user_id:
            cookie_items.append(f"ds_user_id={ds_user_id}")
        if final_sessionid:
            cookie_items.append(f"sessionid={final_sessionid}")

        cookie_string = "; ".join(cookie_items)

        print(f"[ + ] Logged in with @{user}")
        print("[ + ] Session is : ")
        print(final_sessionid or "(not found)")
        print("\n[ + ] Cookies string:")
        print(cookie_string)
        input()
        exit()

    elif "The password you entered is incorrect" in body or "Please check your username and try again." in body or "inactive user" in body or "should_dismiss_loading\", \"has_identification_error\"" in body:
        print("[ - ] Bad Passowrd")
        input()
        exit()
    elif "challenge_required" in body or "two_step_verification" in body:
        print("[ ! ] Challenge requierd acccept and click enter ")
        input()
        login(user,password)
    else:
        print("[ ! ] Something wrong ")
        # طبع الهيدر لو حبيت تشوف Set-Cookie للتصحيح:
        # print(response.headers.get('Set-Cookie'))
        input()
        exit()

if __name__ == "__main__":
    USER = str(input("[ + ] Username : "))
    PASSW = str(input("[ + ] Password : "))
    login(USER,PASSW)

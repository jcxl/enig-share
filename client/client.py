import json
import requests
import base64
import gnupg
import re
import os.path

def get_our_key_info(gpg, regexp):
    private_keys = gpg.list_keys(True)
    our_key = private_keys[0]
    our_uid = our_key['uids'][0]
    our_user_name = regexp.match(our_uid).group(1)
    our_fingerprint = our_key['fingerprint']
    return (our_user_name, our_fingerprint)

def check_key(regexp, key_list, user_name):
    for key in key_list:
        s = regexp.match(key['uids'][0]).group(1)
        if s == user_name:            
            return key
    return None

def auto_key(gpg, regexp, user_name):
    public_keys = gpg.list_keys()
    key = check_key(regexp, public_keys, user_name)
    # encrypt with gpg and sign with private key
    if key is None:
        get_key(user_name)
        key = check_key(regexp, gpg.list_keys(), user_name)
    return key

def put(file_name):
    gpg = gnupg.GPG(gnupghome='gnupg')
    p = re.compile('^(.+) <.*$')
    our_user_name, our_fingerprint = get_our_key_info(gpg, p)
    put_for(our_user_name, file_name)

def put_for(user_name, file_name):

    p = re.compile('^(.+) <.*$')
    g = gnupg.GPG(gnupghome='gnupg')
    our_user_name, our_fingerprint = get_our_key_info(g, p)
    url = 'http://localhost:5000/{}/store/'.format(our_user_name)
    with open(file_name, "rb") as fp:
        bts = fp.read()
        key = auto_key(g, p, user_name)
        if key is None:
            print('User Not Found')
            return
        encrypted_data = g.encrypt(bts,
                                   key['fingerprint'],
                                   sign=our_fingerprint,
                                   armor=False,
                                   #DO NOT FUCKING LEAVE THIS HERE
                                   always_trust=True
                                   )
        b64_bytes = base64.b64encode(encrypted_data.data).decode('utf-8')
        payload = {
            "file_name": os.path.basename(file_name),
            "file_data": b64_bytes,
            "file_target_user": user_name
            }    
        headers = {'content-type': 'application/json'}
        requests.post(url,data=json.dumps(payload), headers=headers)


def get():
    gpg = gnupg.GPG(gnupghome='gnupg')
    p = re.compile('^(.+) <.*$')
    our_user_name, our_fingerprint = get_our_key_info(gpg, p)
    get_from(our_user_name)

def get_from(user_name):
    url = 'http://localhost:5000/{}/retrieve/'.format(user_name)
    r = requests.get(url)
    req_obj = r.json()
    if req_obj['status'] == 'SUCCESS':
        get_key(user_name)
        g = gnupg.GPG(gnupghome='gnupg')
        encrypted_file_data = base64.b64decode(req_obj["data"])
        decrypted_data = g.decrypt(encrypted_file_data)
        # verify that data was signed
        if decrypted_data.signature_id is not None:
            print('Signature verified with ',decrypted_data.trust_text)
            file_name = req_obj["file_name"]
            with open(file_name,"wb") as fp:
                fp.write(decrypted_data.data)
            print('Successfully retrieved file: ', file_name)
        else:
            print('Signature verification failed.')
    else:
        print('Failed: {}'.format(req_obj['error_message']))

def get_private_keyid(gpg):
    return gpg.list_keys(True)[0]['keyid']

def register(user_name):
    url = 'http://localhost:5000/{}/register/'.format(user_name)
    g = gnupg.GPG(gnupghome='gnupg')
    armoured_pub_key = g.export_keys(get_private_keyid(g))
    payload = {
        "user_name" : user_name,
        "public_key" : armoured_pub_key
        }
    headers = {'content-type': 'application/json'}
    requests.post(url,data=json.dumps(payload), headers=headers)

def get_key(user_name):
    url = 'http://localhost:5000/{}/get_key/'.format(user_name)
    r = requests.get(url)
    req_obj = r.json()
    if req_obj['status'] == 'SUCCESS':
        g = gnupg.GPG(gnupghome='gnupg')
        imported_key = g.import_keys(req_obj['public_key'])
        return imported_key
    else:
        print('Failed: {}'.format(req_obj['error_message']))
        return None

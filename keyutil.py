#!/usr/bin/env python
import gnupg
import argparse
import sys

def clean_keys(gpg):
    secret_key = gpg.list_keys(True)[0]
    secret_key_uid = secret_key['uids'][0]

    for key in gpg.list_keys():
        if key['uids'][0] != secret_key_uid:
            gpg.delete_keys(key['fingerprint'])

def list_keys(gpg, private):
    print(gpg.list_keys(private))

if __name__ == "__main__":
    gpg = gnupg.GPG(gnupghome="gnupg")

    if len(sys.argv) > 1:
        if sys.argv[1] == "clean":
            clean_keys(gpg)
        elif sys.argv[1] == "list":
            if len(sys.argv) > 2 and sys.argv[2] == "priv":
                list_keys(gpg, True)
            else:
                list_keys(gpg, False)
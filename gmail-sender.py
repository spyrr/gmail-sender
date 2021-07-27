#!/usr/bin/env python3
import ssl
import time
from colored import *
import sys
import socks
from xsmtplib import SMTP


PORT = 587 
SMTP_SERVER = 'smtp.gmail.com'
SENDER_EMAIL = 'address@gmail.com'  # Enter your address
PASSWORD = 'password'
STATUS_FILENAME = 'status.txt'
MAIL_CONTENTS_FILENAME = 'contents.txt'
"""Mail Contents example
Subject: This is test mail

Hi there,

Morning?

Regards,
"""

C_RED = fg(1)
C_RESET = attr(0)
C_GREEN = fg(2)
C_YELLOW = fg(3)
C_BLUE = fg(4)


def store_status(sended):
    print(f'[*] store current status to "{C_RED}{STATUS_FILENAME}{C_RESET}"')
    sended = set(sended)
    with open(STATUS_FILENAME, 'w') as f:
        f.write('\n'.join(m for m in sended) + '\n')
    print(f'[*] {len(sended)} emails were stored to {STATUS_FILENAME}')


def load_status():
    sended = []
    try:
        print(f'[*] Load status file')
        with open(STATUS_FILENAME, 'r') as f:
            sended = f.read().strip().split('\n')
        print(f'[*] {len(sended)} emails were loaded')
    except:
        print(f'{C_RED}[ERROR]{C_RESET} There is no status file')
    return sended


def load_receiver(filename='emails.txt'):
    receivers = []

    try:
        print(f'[*] Load receiver list from {filename}')
        with open(filename, 'r') as f:
            receivers = f.read().strip().split('\n')
        print(f'[*] {len(receivers)} emails were loaded')
    except:
        print(f'{C_RED}[ERROR]{C_RESET} There is no file, {filename}')
    return receivers


def main():
    message = ''
    with open(MAIL_CONTENTS_FILENAME, 'r') as f:
        message = f.read().encode('utf8')

    context = ssl.create_default_context()
    sended = load_status()
    receivers = load_receiver(sys.argv[1])

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.set_ciphers('ECDH+AESGCM')
    context.set_default_verify_paths()
    context.verify_mode = ssl.CERT_REQUIRED

    with SMTP(
        SMTP_SERVER, PORT, proxy_host='127.0.0.1', proxy_port=9050,
        proxy_type=socks.SOCKS5, timeout=30
    ) as server:
        if server.starttls(context=context)[0] != 220:
            print(f'{C_RED}[ERROR]{C_RESET} starttls != 220')
            sys.exit(-2)

        server.login(SENDER_EMAIL, PASSWORD)
        for i in range(len(receivers)):
            try:
                receiver = receivers[i].strip()
                if receiver in sended:  # Skip for sended receiver
                    print(
                        f'[{i}] "{C_GREEN}{receiver}{C_RESET}"'
                        + f' - {C_YELLOW}skip{C_RESET}'
                    )
                    continue

                print(f'[{i}] Send to "{C_GREEN}{receiver}{C_RESET}"')
                server.sendmail(SENDER_EMAIL, receiver, message)
                sended.append(receiver)
                time.sleep(0.5)
            except:
                print(
                    f'{C_RED}[ERROR]{C_RESET} failed to send to '
                    + f' "{C_GREEN}{receiver}{C_RESET}"'
                )
                store_status(sended)
                sys.exit(-1)
        store_status(sended)


if __name__ == '__main__':
    main()

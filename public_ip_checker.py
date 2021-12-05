"""
This script will check public ip every hour so that in case of a change in public ip,
it will send me a mail of the new one. 

Be aware that this creates a sqlite3 database to log last ips.

Could have been made to be modular but I preferred a standalone script.
"""

from subprocess import check_output
import smtplib, ssl, os
from datetime import datetime
import sqlite3
import logging
from configparser import ConfigParser

#Decodes strings from binary to ascii
#Input is list incase other things are later added
def decode_str(strings):
        decoded = []
        for string in strings:
                decoded.append(string.decode('ascii'))
        return decoded

def get_public_ip():
    pub_ip = check_output(['curl', 'ifconfig.me'])

    #check_output method returns binary strings
    pub_ip, = decode_str([pub_ip])

    return pub_ip

def send_mail(time, pub_ip):
    #smtp requirements from info.cfg
    parser = ConfigParser()
    parser.read('info.cfg')

    port = '{}'.format(parser.get('mail', 'port'))
    passwd = '{}'.format(parser.get('mail', 'passwd'))
    sender_email = '{}'.format(parser.get('mail', 'sender'))
    receiver_email = '{}'.format(parser.get('mail', 'receiver'))

    message = """

        Subject: RP Server - Public IP Has Been Changed

        Hign's server detected a change in public ip adress on datetime {}.

        Current public ip : {}

        """

    #Sending email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(sender_email, passwd)
            server.sendmail(sender_email, receiver_email, message.format(time, pub_ip))

#Checks if the db exists, if not, creates db and table
def check_db_and_connect():
    if not os.path.isfile('public_ip_logs.db'):
        conn = sqlite3.connect('/home/ubuntu/Documents/Scripts/public_ip_checker/public_ip_logs.db')
        create_table_public_ip_logs(conn)
    else:
        conn = sqlite3.connect('public_ip_logs.db')

    return conn

def create_table_public_ip_logs(conn):
    conn.execute("""
        CREATE TABLE public_ip_logs
        (
            ip TEXT NOT NULL,
            datetime_checked TEXT
        );
    """)

def check_last_public_ip(conn):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM public_ip_logs ORDER BY datetime_checked DESC LIMIT 1;
    """)
    try:
        last_logged_ip = cursor.fetchone()[0]
    except:
        last_logged_ip = None
    cursor.close()

    return last_logged_ip

def insert_log(conn, values):
    query = """
        INSERT INTO public_ip_logs (ip, datetime_checked) VALUES ('{}', '{}')
    """
    conn.execute(query.format(values['ip'], values['time']))
    conn.commit()

if __name__ == '__main__':
    #Logger
    logging.basicConfig(level=logging.INFO, filemode='a', format="%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s", filename='pub_ip_checker.log')
    logging.info('Public ip checker starting.')

    db_conn = check_db_and_connect()

    try:
        pub_ip = get_public_ip()
    except Exception as e:
        logging.error('Public ip could not be read || Exception: {}'.join(str(e)))

    time = datetime.now().strftime('%Y.%m.%d %H:%M:%S')

    last_logged_ip = check_last_public_ip(db_conn)
    if last_logged_ip == None:
        insert_log(db_conn, {'ip':pub_ip, 'time':time})
    elif last_logged_ip == pub_ip:
        logging.info('Public ip checked, has not been changed. Skipping.')
    else:
        insert_log(db_conn, {'ip':pub_ip, 'time':time})
        try:
            send_mail(time, pub_ip)
            logging.info('Dynamic ip change has been detected. Mail has been sent.')
        except Exception as e:
            logging.error('Different ip has been detected but mail could not be sent || Exception: {}'.join(str(e)))

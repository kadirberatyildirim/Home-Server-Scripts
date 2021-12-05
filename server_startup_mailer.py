"""
This script will run when server reboots.

I have added some information to be sent via mail, which alerts me of a reboot.

Give some time after reboot so that in a power outage, your router will have time
to connect to the internet.
"""

from subprocess import check_output
import smtplib, ssl
from datetime import datetime
from configparser import ConfigParser

def decode_str(strings):
        decoded = []
        for string in strings:
                decoded.append(string.decode('ascii'))
        return decoded

#Information to be gathered and sent
who = check_output(['who'])
pub_ip = check_output(['curl', 'ifconfig.me'])
disk_usage = check_output(['df', '-h', '/home'])
last_logins = check_output(['lastlog', '-t', '10000'])
#Decode strings from binary to ascii
pub_ip, disk_usage, last_logins = decode_str([pub_ip, disk_usage, last_logins])

time = datetime.now().strftime('%Y.%m.%d %H:%M:%S')


#smtp requirements
parser = ConfigParser()
parser.read('info.cfg')

port = '{}'.format(parser.get('mail', 'port'))
passwd = '{}'.format(parser.get('mail', 'passwd'))
sender_email = '{}'.format(parser.get('mail', 'sender'))
receiver_email = '{}'.format(parser.get('mail', 'receiver'))

message = """

Subject: RP Server Information on Reboot

Hign's server has been rebooted on datetime {}.

Disk Usage (/Home):
{}

Current public ip : {}

Last logins of each user:
{}

"""

#Sending email
context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, passwd)
        server.sendmail(sender_email, receiver_email, message.format(time, disk_usage, pub_ip, last_logins))

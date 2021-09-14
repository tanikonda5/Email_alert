import base64
import datetime
import pdb
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTPException
import cx_Oracle
import pandas as pd


def open_database_connection():
    connection_string = '' + "/" + '' + \
                        "@" + '' + ":" + '' + \
                        "/" + ''

    conn = cx_Oracle.connect(connection_string)

    return conn


def get_token_data():
    conn = open_database_connection()
    cur = conn.cursor()

    query = "Select token, token_expiration_date, secret_key_path from vault where active_flag=1"
    cur.execute(query)
    token_data = pd.DataFrame(cur.fetchall())
    token_data.rename(columns={0: 'Token',
                               1: 'Token_expiration_date',
                               2: 'Secret_key_path'},
                      inplace=True)

    sorted_df = token_data.sort_values(by=['Token_expiration_date'])
    token_dic = sorted_df.T.to_dict()

    return token_dic


def send_email(tolist, subject, msgbody):
    """
    Send an email to specific list of users

    : param tolist: list of emails to send the specific email too
    : param subject: subject of the email being sent
    : param msgbody : the message body of the email to be sent
    """

    msg = MIMEMultipart()
    message = msgbody
    msgfrom = 'sivadheeraj57@gmail.com'
    msg['Subject'] = subject
    msg['From'] = msgfrom
    msg['To'] = tolist

    msg.attach(MIMEText(message, 'plain'))
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login('sivadheeraj57@gmail.com', '9902532141')
    s.sendmail(msgfrom, tolist.split(","), msg.as_string())
    s.quit()
    return "Message sent!"


def token_decryption(encrypted_token):
    token_decode = base64.decodebytes(encrypted_token.encode('utf-8'))
    decrypted_token = token_decode.decode()
    return decrypted_token


data = get_token_data()
expired_tokens = []

for i in data:
    days_left = (data[i]['Token_expiration_date'] - datetime.datetime.now()).days
    if days_left <= 15:
        expired_tokens += [
            token_decryption(data[i]['Token']) + "\t||\t" + data[i]['Secret_key_path'] + "\t||\t" + str(days_left)]
content = "Token\t||\tSecret_Key_Path\t||\tAbout_to_Expire\n"
for i in expired_tokens:
    content += "\n" + i + "\n"

send_email("sai.tanikonda@gmail.com", "Attention! some tokens are about to expire", content)

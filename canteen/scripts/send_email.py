# -*- coding: utf-8 -*-
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django3_apps.settings import BASE_DIR
from django.conf import settings
import datetime


def run():
    day = str(datetime.date.today())
    email_sender = settings.EMAIL_HOST_USER
    email_to = []
    email_bcc = []

    subject = 'Viessmann, orders for the day ' + day

    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = ",".join(email_to)
    msg['Bcc'] = ",".join(email_bcc)
    msg['Subject'] = subject

    body = 'This message has been generated automatically. Please do not respond'
    msg.attach(MIMEText(body, 'plain'))

    filename = BASE_DIR + '/canteed/reports/' + day + '.csv'
    attachment = open(filename, 'rb')

    part = MIMEBase('application', 'octet_stream')

    part.set_payload((attachment).read())

    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename=" + day + '.csv')

    msg.attach(part)
    text = msg.as_string()

    email_send = email_to + email_bcc

    connection = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    connection.starttls()
    connection.login(email_sender, settings.EMAIL_HOST_PASSWORD)
    connection.sendmail(email_sender, email_send, text)
    connection.quit()

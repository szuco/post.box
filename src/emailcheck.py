import time
from itertools import chain
import email
import imaplib
import mailparser


imap_ssl_host = 'imap.gmx.net'
#imap_ssl_host = 'mx.freenet.de'

imap_ssl_port = 993
username = 'piotr.szegvari@gmx.de'
#username = 'icebreaker@freenet.de'

password = 'szuco_gmx'
#password = 'Szuco-0-Freenet'


# Restrict mail search. Be very specific.
# Machine should be very selective to receive messages.
criteria = {
    'SUBJECT': 'DPD',
    'BODY':    'Sendung',
}
uid_max = 0


def search_string(uid_max, criteria):
    c = list(map(lambda t: (t[0], '"'+str(t[1])+'"'), criteria.items())) + [('UID', '%d:*' % (uid_max+1))]
    return '(%s)' % ' '.join(chain(*c))
    # Produce search string in IMAP format:
    #   e.g. (FROM "me@gmail.com" SUBJECT "abcde" BODY "123456789" UID 9999:*)


def get_first_text_block(msg):
    type = msg.get_content_maintype()

    if type == 'multipart':
        for part in msg.get_payload():
            if part.get_content_maintype() == 'text':
                return part.get_payload()
    elif type == 'text':
        return msg.get_payload()


server = imaplib.IMAP4_SSL(imap_ssl_host, imap_ssl_port)
server.login(username, password)
server.select('INBOX')

result, data = server.uid('search', None, search_string(uid_max, criteria))

uids = [int(s) for s in data[0].split()]
#if uids:
    #uid_max = max(uids)
    # Initialize `uid_max`. Any UID less than or equal to `uid_max` will be ignored subsequently.

server.logout()


# Keep checking messages ...
# I don't like using IDLE because Yahoo does not support it.
while 1:
    # Have to login/logout each time because that's the only way to get fresh results.

    server = imaplib.IMAP4_SSL(imap_ssl_host, imap_ssl_port)
    server.login(username, password)
    server.select('INBOX')

    #result, data = server.uid('search', None, search_string(uid_max, criteria))
    result, data = server.uid('search', None, "ALL")

    #uids = [int(s) for s in data[0].split()]
    #for uid in uids:
        
    for uid in data[0].split():
        # Have to check again because Gmail sometimes does not obey UID criterion.
        if int(uid) > uid_max:
            result, msg_data = server.uid('fetch', uid, '(RFC822)')  # fetch entire message

            mail = mailparser.parse_from_string(str(msg_data[0][1]))
            c = mail.body
            if c:
                print(c)
            #msg = email.message_from_string(str(msg_data[0][1]))
            #uid_max = uid
            #text = get_first_text_block(msg)
            #print('New message :::::::::::::::::::::')
            #print(text)
    server.logout()
    time.sleep(1)

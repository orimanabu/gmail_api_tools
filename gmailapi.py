#!/usr/bin/python
# vi: set et sts=4 sw=4 ts=4 :

import re
import certifi
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from apiclient.discovery import build
from pprint import pprint
import base64

def auth():
    scope = 'https://www.googleapis.com/auth/gmail.readonly'
    redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
    user_agent = 'orimanabu'
    secret_file = 'client_secret.json'
    cred_file = 'cred.json'

    flow = flow_from_clientsecrets(secret_file, scope=scope, redirect_uri=redirect_uri)
    storage = Storage(cred_file)
    cred = storage.get()
    if cred is None or cred.invalid:
        auth_uri = flow.step1_get_authorize_url()
        print 'Please go to this URL and get an authentication code:'
        print auth_uri
        print
        code = raw_input('Please input the authentication code here:')
        h = httplib2.Http(ca_certs=certifi.where())
        cred = flow.step2_exchange(code, http=h)
        storage.put(cred)
    return cred

def gmail_connect(cred):
    http = httplib2.Http(ca_certs=certifi.where())
    http = cred.authorize(http)

    # Build the Gmail service from discovery
    gmail = build('gmail', 'v1', http=http)
    return gmail

def subroutine(gmail):
    # Retrieve a page of threads
    threads = gmail.users().threads().list(userId='me').execute()

    # Print ID for each thread
    if threads['threads']:
        for thread in threads['threads']:
            print 'Thread ID: %s' % (thread['id'])
            obj = gmail.users().threads().get(userId='me', id=thread['id']).execute()
            msg = obj['messages'][0]
            headers = msg['payload']['headers']
            for header in headers:
                if header['name'] == 'Subject':
                    print('  Subject: %s' % header['value'])
                    print('  Snippet: %s' % msg['snippet'])
            #pprint(msg['payload'])
            #print('  body data: %s' % msg['payload']['body']['data'])
            #if isinstance(msg['payload'], list):
            #    print('  *** payload is list')
            #else:
            #    print('  *** payload is not list')
            data = None
            if msg['payload'].get('parts'):
                print('  *** payload has parts')
                i = 0
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        #print('  body[%d]: %s' % (i, part['body']['data']))
                        i = i + 1
                        data = part['body']['data']
                        break
            else:
                print('  *** payload has not parts')
                #print('  body: %s' % msg['payload']['body']['data'])
                #print('  mimeType: %s' % msg['payload']['mimeType'])
                data = msg['payload']['body']['data']
            #print('  data: [%s]' % data)
            print('vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv')
            print(base64.urlsafe_b64decode(str(data)))
            print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')

if __name__ == '__main__':
    gmail = gmail_connect(auth())
    subroutine(gmail)

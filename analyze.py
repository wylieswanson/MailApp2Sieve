#!/usr/bin/env python

import json
import plistlib

stmt = 'if'
p = plistlib.readPlist(
    '/Volumes/Storage/Users/wylie/Library/Mail/V3/MailData/SyncedRules.plist')


def handle(header, expression, mbox):
    global stmt
    if header in ('To', 'Cc', 'From'):
        print stmt, \
            'address :contains ["%s"]  "%s" { fileinto "INBOX.%s"; }' % (
                header, expression, mbox)
    elif header == 'Subject':
        print stmt, \
            'header :matches "Subject" ["*%s*"] { fileinto "INBOX.%s"; }' % (
                expression, mbox)
    else:
        raise ValueError(header)
    stmt = 'elsif'

j = json.dumps(p, sort_keys=True, indent=2, separators=(',', ': '))
print j

print len(p)

print '''
require ["fileinto", "reject"];
'''

"""
for rule in p['rules']:
    if 'Mailbox' not in rule: continue
    mbox = rule['Mailbox'].split('/')[-1].split('.')[0]
    print '#', rule['RuleName'], '->', mbox
    for criteria in rule['Criteria']:
        if criteria['Header'] == 'AnyRecipient':
            handle('To', criteria['Expression'], mbox)
            handle('Cc', criteria['Expression'], mbox)
        else:
            handle(criteria['Header'], criteria['Expression'], mbox)
            """

for rule in p:
    if 'Mailbox' not in rule:
        continue
    mbox = rule['Mailbox'].split('/')[-1].split(',')[0]
    print "#", rule['RuleName'], '->', mbox
    for criteria in rule['Criteria']:
        if criteria['Header'] == 'AnyRecipient':
            handle('To', criteria['Expression'], mbox)
            handle('Cc', criteria['Expression'], mbox)
        else:
            handle(criteria['Header'], criteria['Expression'], mbox)


print '''
else {
keep;
}
'''

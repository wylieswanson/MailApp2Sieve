#!/usr/bin/env python

import json
import plistlib
from urlparse import urlparse
from urllib import unquote

stmt = 'if'
p = plistlib.readPlist(
    '/Volumes/Storage/Users/wylie/Library/Mail/V4/MailData/SyncedRules.plist')


def handle_any(header, expression, mbox):
    global stmt
    if header in ('To', 'Cc', 'From'):
        print stmt, \
            'address :contains ["%s"] ["%s"] {\n' \
            '\tfileinto "%s";\n}' % (
                header, expression, mbox)
    elif header == 'Subject':
        print stmt, \
            'header :matches "Subject" ["*%s*"] {\n' \
            '\tfileinto "%s";\n}' % (
                expression, mbox)
    else:
        raise ValueError(header)
    stmt = 'elsif'


def handle_specific(criteria, mbox):
    matches = []
    print "elsif allof ("

    for criteria in rule['Criteria']:
        if 'Qualifier' in criteria:
            if criteria['Header'] in ('To', 'Cc', 'From'):
                matches.append('\tnot address :contains ["%s"]  "%s"' % (
                    criteria['Header'], criteria['Expression']))
            elif criteria['Header'] == 'Subject':
                matches.append('\tnot header :matches "Subject" ["*%s*"]' % (
                    criteria['Expression']))
        else:
            if criteria['Header'] in ('To', 'Cc', 'From'):
                matches.append('\taddress :contains ["%s"]  "%s"' % (
                    criteria['Header'], criteria['Expression']))
            elif criteria['Header'] == 'Subject':
                matches.append('\theader :matches "Subject" ["*%s*"]' % (
                    criteria['Expression']))

    print ",\n".join(matches)
    print ') {\n\tfileinto "%s"\n}' % (mbox)


j = json.dumps(p, sort_keys=True, indent=2, separators=(',', ': '))

print 'require ["fileinto", "reject"];'

for rule in p:
    if 'CopyToMailboxURL' not in rule:
        continue
    mbox = unquote(
        urlparse(rule['MailboxURL']).path).decode('utf8').strip('/')
    print "\n# \"", rule['RuleName'], '\"\n#  ->', \
        mbox, rule['AllCriteriaMustBeSatisfied']
    if rule['AllCriteriaMustBeSatisfied'] is False:
        for criteria in rule['Criteria']:
            if 'AnyMessage' in criteria['Header']:
                continue
            if criteria['Header'] == 'AnyRecipient':
                handle_any(
                    'To', criteria['Expression'], mbox)
                handle_any(
                    'Cc', criteria['Expression'], mbox)
            else:
                handle_any(
                    criteria['Header'], criteria['Expression'], mbox)
    elif rule['AllCriteriaMustBeSatisfied'] is True:
        handle_specific(rule['Criteria'], mbox)

print "else {\n\tkeep;\n}"

# print j, len(p)

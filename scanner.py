#!/usr/bin/python

import sys
import getopt
import requests
import yaml
import time
import random

def test_url(url, success_codes):
  r = requests.get(url)
  if r.status_code in success_codes:
    result = {
      'code': r.status_code,
      'url': url,
      'headers': []
    }
    for key in r.headers:
      result['headers'].append((key, r.headers[key]))
    return result

def wrap(prefixes, postfixes, string, ignore_blank = False):
  for prefix in prefixes:
    for postfix in postfixes:
      if ignore_blank and prefix == '' and postfix == '':
        continue
      yield prefix + string + postfix

opts, args = getopt.getopt(sys.argv[1:], 'hsu:', ['simulate', 'url='])
url = ''
simulate = False
for opt, arg in opts:
  if opt == '-h':
    print 'scanner.py [-s/--simulate] -u <url>'
    sys.exit()
  elif opt in ('-s', '--simulate'):
    simulate = True
  elif opt in ('-u', '--url'):
    url = arg + ('/' if not arg.endswith('/') else '')
if not url:
  print 'scanner.py [-s/--simulate] -u <url>'
  sys.exit()

stream = file('list.yaml', 'r')
config = yaml.load(stream)
stream.close()

to_test = []

for section in config:
  entries = config[section]['Entries']
  prefixes = config[section]['Prefixes'] or ['']
  postfixes = config[section]['Postfixes'] or ['']
  ignore_blank = config[section]['IgnoreBlank']
  success_codes = config[section]['SuccessCodes']
  for directory in entries:
    for wrapped_directory in wrap(prefixes, postfixes, directory, ignore_blank):
      to_test.append((url + wrapped_directory, success_codes))

random.shuffle(to_test)

if simulate:
  for url,success_code in to_test:
    print url
  print '%d urls in total' % len(to_test)
  sys.exit()

found = 0
i = 0
for url,success_codes in to_test:
  i += 1
  result = test_url(url, success_codes)
  sys.stdout.write(chr(27) + '[0G') # Move to col 0
  sys.stdout.write(chr(27) + '[0K') # Clear from cursor
  sys.stdout.flush()
  if result:
    found += 1
    print 'HTTP %d: %s' % (result['code'], result['url'])
    for key,value in result['headers']:
      print '  %s: %s' % (key, value)
  sys.stdout.write('%.1f %%, %d urls remaining, %d found' % (float(i) / len(to_test) * 100.0, len(to_test) - i, found))
  sys.stdout.flush()

sys.stdout.write(chr(27) + '[0G') # Move to col 0
sys.stdout.write(chr(27) + '[0K') # Clear from cursor

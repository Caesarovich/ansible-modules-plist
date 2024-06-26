#!/usr/bin/python
#
# (c) 2015, Matthias Neugebauer

DOCUMENTATION = '''
---
module: plist_file
author: Matthias Neugebauer
short_description: Manage settings in plist files
description:
  - Manage settings in plist files.
options:
  dest:
    description:
      - Domain or absolut path to the plist file; file will be created if required.
    required: true
    default: null
  value:
    description:
      - Value which sould be set.
    required: true
    default: null
  key:
    description:
      - Key to manage.
    required: false
    default: null
requirements: [ "biplist" ]
'''

EXAMPLES = '''
plist_file:
  dest: /tmp/ansible.modules.plist.test.plist
  key: testString
  value: myString

plist_file:
  dest: ansible.modules.plist.test
  key: testInt
  value: 7
'''

import sys
import collections.abc as collections



try:
    import biplist
except ImportError:
    print("failed=True msg='biplist required for this module'")
    sys.exit(1)

def do_plist(module, filename, value, key=None):
    working_value = value if key == None else {key: value}
    changed = False

    try:
        f = open(filename, 'rb')
        plist = biplist.readPlist(f)
    except:
        plist = dict()
    finally:
        f.close()
    

    changed = not equal(plist, working_value)

    if changed and not module.check_mode:
        try:
            update(plist, working_value)
            f = open(filename, 'wb')
            biplist.writePlist(plist, f)
        except Exception as e:
            module.fail_json(msg="Can't change %s" % filename, error=str(e))
        finally:
            f.close()

    return changed

def equal(slave, master):
    if isinstance(slave, collections.Mapping) and isinstance(master, collections.Mapping):
        for k, v in master.items():
            if not equal(slave.get(k), v):
                return False
    else:
        return master == slave

    return True

def update(d, u):
    """Taken from http://stackoverflow.com/a/3233356"""
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d

def main():
    module = AnsibleModule(
        argument_spec = dict(
            dest  = dict(required=True),
            value = dict(required=True, type='raw'),
            key   = dict(required=False)
        ),
        supports_check_mode=True
    )

    if not module.params['dest'].startswith('/'):
        module.params['dest'] = os.path.expanduser("~/Library/Preferences/%s.plist" % module.params['dest'])

    dest  = module.params['dest']
    key   = module.params['key']
    value = module.params['value']

    changed = do_plist(module, dest, value, key)

    module.exit_json(dest=dest, changed=changed, msg="OK")

from ansible.module_utils.basic import *
main()

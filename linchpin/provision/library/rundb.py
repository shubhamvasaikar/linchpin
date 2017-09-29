#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import json

from ansible.module_utils.basic import AnsibleModule

from linchpin.rundb import DB_SCHEMA
from linchpin.rundb.basedb import BaseDB
from linchpin.rundb.drivers import DB_DRIVERS

# ---- Documentation Start ----------------#
DOCUMENTATION = '''
---
version_added: "0.1"
module: run_db
short_description: A run database for linchpin, though it could be used for anything transactional really.
description:
  - This module allows a user to store and retrive values.
options:
  db_type:
    description:
      Type of Database used
    required: false
    default: TinyRunDB
  conn_str:
    description:
      Connection string to the database, can be file or url
    required: true
  operation:
    description:
      Operation being performed on the database
      Available operations: init, update, purge, search
    required: true
    default: update
  run_id:
    description: The run_id value describes the current transaction.
                 The run_id is returned from an 'init' operation.
                 The run_id is required for an 'update' operation.
    required: false
    default: None
  table: (aka target in linchpin)
    description:
      Name of the table to update in the database
    required: true
  action:
    description:
      Action being performed, up/destroy
    required: false
    default: up
  key:
    description:
      key for the db record
    required: true (except for init and purge operations)
  value:
    description:
      value for the db record. Must be a dictionary of values.
    required: true (except for init and purge operations)

example


requirements: [TinyDB (or your own database)]
author: Clint Savage - herlo@redhat.com
'''


def main():

    module = AnsibleModule(
        argument_spec=dict(
            db_type=dict(type='str', required=False, default='TinyRunDB'),
            conn_str=dict(type='str', required=True),
            operation=dict(choices=['init',
                                 'update',
                                 'purge',
                                 'search'],
                        default='update'),
            run_id=dict(type='int', required=False),
            table=dict(type='str', required=True),
            action=dict(type='str', required=False, default='up'),
            key=dict(type='str', required=False),
            value=dict(type='dict', required=False)
        ),
    )
    db_type = module.params['db_type']
    conn_str = os.path.expanduser(module.params['conn_str'])
    table = module.params['table']
    action = module.params['action']
    op = module.params['operation']
    key = module.params['key']
    value = module.params['value']

    is_changed = False
    try:
        run_db = BaseDB(DB_DRIVERS[db_type], conn_str=conn_str)

        if op in ['init', 'purge']:
            if op == "init":

                DB_SCHEMA['action'] = action
                output = run_db.init_table(table, DB_SCHEMA)
                if output:
                    is_changed = True

        else:
            msg = ("Module 'action' required".format(action))
            module.fail_json(msg=msg)

        run_db.close()
        module.exit_json(output=output, changed=is_changed)

    except Exception as e:
        module.fail_json(msg=str(e))


#        if op == "purge":
#            output = run_db.purge(table=target)
#
#    if op in ['update','search']:
#
#        if action == "update":
#            if run_id and key and value:
#                output = run_db.update_record(table, run_id, key, value)
#            else:
#                msg = ("'table', 'run_id, 'key', and 'value' required"
#                       " for update operation")
#                module.fail_json(msg=msg)
#
#        if op == "search":
#            output = "noop"
#
#            module.exit_json(output=output, changed=output)
#        except Exception as e:
#            module.fail_json(msg=str(e))


# ---- Import Ansible Utilities (Ansible Framework) -------------------#
main()

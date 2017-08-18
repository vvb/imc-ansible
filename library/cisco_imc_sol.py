#!/usr/bin/python

# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import (absolute_import, division, print_function)
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: cisco_imc_sol
short_description: Configures SOL on a Cisco IMC server
version_added: "2.4"
description:
    - Configures the Serial Over Lan(SOL) service on a Cisco IMC server
Input Params:
    state:
        description:
         - if C(present), enable and configure SOL
         - if C(absent), disable SOL
        choices: ['present', 'absent']
        default: "present"
    speed:
        description: speed of the connection
        choices: ["9600", "19200", "38400", "57600", "115200"]

    comport:
        description: Comport on the server side
        choices: ["com0", "com1"]

    server_id:
        description: Server Id to be specified for C3260 platforms
        choices: ["admin", "read-only", "user"]

    ssh_port:
        description: the SSH port for access to the console

requirements:
    - 'imcsdk'
    - 'python2 >= 2.7.9 or python3 >= 3.2'
    - 'openssl version >= 1.0.1'

author: "Cisco Systems Inc(ucs-python@cisco.com)"
'''


EXAMPLES = '''
- name: enable SOL over ssh
  cisco_imc_sol:
    comport: "com0"
    speed: "115200"
    ssh_port: 22
    state: present
    ip: "192.168.1.1"
    username: "admin"
    password: "password"
'''

RETURN = ''' # '''


def _argument_mo():
    return dict(
        speed=dict(
            type='str',
            choices=["9600", "19200", "38400", "57600", "115200"]),
        comport=dict(
            type='str',
            choices=["com0", "com1"]),
        ssh_port=dict(
            type='str'),
        server_id=dict(type='int',
                       default=1),
    )


def _argument_custom():
    return dict(
        state=dict(default="present",
                   choices=['present', 'absent'],
                   type='str'),
    )


def _argument_connection():
    return dict(
        # ImcHandle
        imc_server=dict(type='dict'),

        # Imc server credentials
        imc_ip=dict(type='str'),
        imc_username=dict(default="admin", type='str'),
        imc_password=dict(type='str', no_log=True),
        imc_port=dict(default=None),
        imc_secure=dict(default=None),
        imc_proxy=dict(default=None),
        starship_options=dict(required=False, type='dict', default=None)
    )


def _ansible_module_create():
    argument_spec = dict()
    argument_spec.update(_argument_mo())
    argument_spec.update(_argument_custom())
    argument_spec.update(_argument_connection())

    return AnsibleModule(argument_spec,
                         supports_check_mode=True)


def _get_mo_params(params):
    args = {}
    for key in _argument_mo():
        if params.get(key) is None:
            continue
        args[key] = params.get(key)
    return args


def setup_module(server, module):
    from imcsdk.apis.server.sol import sol_enable
    from imcsdk.apis.server.sol import sol_disable
    from imcsdk.apis.server.sol import sol_exists

    ansible = module.params
    args_mo = _get_mo_params(ansible)
    exists, mo = sol_exists(handle=server, **args_mo)

    if ansible["state"] == "present":
        if module.check_mode or exists:
            return not exists
        sol_enable(handle=server, **args_mo)
    else:
        if module.check_mode or not exists:
            return exists
        sol_disable(server)
    return True


def setup(server, module):
    result = {}
    err = False

    try:
        result["changed"] = setup_module(server, module)
    except Exception as e:
        err = True
        result["msg"] = "setup error: %s" % str(e)
        result["changed"] = False

    return result, err


def main():
    from ansible.module_utils.cisco_imc import ImcConnection

    module = _ansible_module_create()
    conn = ImcConnection(module)
    server = conn.login()
    result, err = setup(server, module)
    conn.logout()
    if err:
        results["status"] = "error"
        module.fail_json(**result)
    else:
        results["msg"] = "" 
        results["status"] = "ok" 
    module.exit_json(**result)


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2015, Cumulus Networks <ce-ceng@cumulusnetworks.com>
#
# This file is part of Ansible
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: cl_quagga_ospf
author: "Cumulus Networks (ce-ceng@cumulusnetworks.com)"
short_description: Configure basic OSPFv3 parameters and interfaces using Quagga
description:
    - Configures basic OSPFv3 global parameters such as
      router id and bandwidth cost, or OSPFv3 interface configuration like
      point-to-point settings or enabling OSPFv3 on an interface. Configuration
      is applied to single OSPFv2 instance. Multiple OSPFv3 instance
      configuration is currently not supported. It requires Quagga version
      0.99.22 and higher with the non-modal Quagga CLI developed by Cumulus
      Linux. For more details go to the Routing User Guide at
      http://docs.cumulusnetworks.com/ and Quagga Docs at
      http://www.nongnu.org/quagga/
options:
    router_id:
        description:
            - Set the OSPFv3 router id
        required: true
    saveconfig:
        description:
            - Boolean. Issue write memory to save the config
        choices: ['yes', 'no']
        default: ['no']
    interface:
        description:
            - define the name the interface to apply OSPFv3 services.
    point2point:
        description:
            - Boolean. enable OSPFv3 point2point on the interface
        choices: ['yes', 'no']
        require_together:
            - with interface option
    area:
        description:
            - defines the area the interface is in
        required_together:
            - with interface option
    passive:
        description:
            - make OSPFv3 interface passive
        choices: ['yes', 'no']
        required_together:
            - with interface option
    state:
        description:
            - Describes if OSPFv3 should be present on a particular interface.
              Module currently does not check that interface is not associated
              with a bond or bridge. User will have to manually clear the
              configuration of the interface from the bond or bridge. This will
              be implemented in a later release
        choices: [ 'present', 'absent']
        default: 'present'
        required_together:
            - with interface option
requirements:  ['Cumulus Linux Quagga non-modal CLI, Quagga version 0.99.22 and higher']
'''
EXAMPLES = '''
Example playbook entries using the cl_quagga_ospf module

    tasks:
    - name: configure ospf router_id
        cl_quagga_ospf: router_id=10.1.1.1
    - name: enable OSPFv3 on swp1 and set it be a point2point OSPF
      interface with a cost of 65535
        cl_quagga_ospf: interface=swp1 point2point=yes cost=65535
    - name: enable ospf on swp1-5
        cl_quagga_ospf: interface={{ item }}
        with_sequence: start=1 end=5 format=swp%d
    - name: disable ospf on swp1
        cl_quagga_ospf: interface=swp1 state=absent
'''


def run_cl_cmd(module, cmd, check_rc=True, split_lines=True):
    try:
        (rc, out, err) = module.run_command(cmd, check_rc=check_rc)
    except Exception, e:
        module.fail_json(msg=e.strerror)
    # trim last line as it is always empty
    if split_lines:
        ret = out.splitlines()
    else:
        ret = out
    return ret


def check_dsl_dependencies(module, input_options,
                           dependency, _depend_value):
    for _param in input_options:
        if module.params.get(_param):
            if not module.params.get(dependency):
                _param_output = module.params.get(_param)
                _msg = "incorrect syntax. " + _param + " must have an interface option." + \
                    " Example 'cl_quagga_ospf6: " + dependency + "=" + _depend_value + " " + \
                    _param + "=" + _param_output + "'"
                module.fail_json(msg=_msg)


def has_interface_config(module):
    if module.params.get('interface') is not None:
        return True
    else:
        return False


def get_running_config(module):
    running_config = run_cl_cmd(module, '/usr/bin/vtysh -c "show run"')
    got_global_config = False
    got_interface_config = False
    module.interface_config = {}
    module.global_config = []
    for line in running_config:
        line = line.lower().strip()
        # ignore the '!' lines or blank lines
        if len(line.strip()) <= 1:
            if got_global_config:
                got_global_config = False
            if got_interface_config:
                got_interface_config = False
            continue
        # begin capturing global config
        m0 = re.match('router\s+ospf6', line)
        if m0:
            got_global_config = True
            continue
        m1 = re.match('^interface\s+(\w+)$', line)
        if m1:
            module.ifacename = m1.group(1)
            module.interface_config[module.ifacename] = []
            got_interface_config = True
            continue
        if got_interface_config:
            module.interface_config[module.ifacename].append(line)
            continue
        if got_global_config:
            m3 = re.match('\s*passive-interface\s+(\w+)', line)
            m4 = re.match('^interface\s+(\w+)\s+(area\s+[0-9.]+)', line)
            if m3:
                ifaceconfig = module.interface_config.get(m3.group(1))
                if ifaceconfig:
                    ifaceconfig.append('passive-interface')
            if m4:
                ifaceconfig = module.interface_config.get(m4.group(1))
                if ifaceconfig:
                    ifaceconfig.append(m4.group(2))
            else:
                module.global_config.append(line)
            continue


def get_config_line(module, stmt, ifacename=None):
    if ifacename:
        pass
    else:
        for i in module.global_config:
            if re.match(stmt, i):
                return i
    return None


def update_router_id(module):
    router_id_stmt = 'router-id '
    actual_router_id_stmt = get_config_line(module, router_id_stmt)
    router_id_stmt = 'router-id ' + module.params.get('router_id')
    if router_id_stmt != actual_router_id_stmt:
        cmd_line = "/usr/bin/cl-ospf6 router-id set %s" %\
                   (module.params.get('router_id'))
        run_cl_cmd(module, cmd_line)
        module.exit_msg += 'router-id updated '
        module.has_changed = True


def add_global_ospf_config(module):
    module.has_changed = False
    get_running_config(module)
    if module.params.get('router_id'):
        update_router_id(module)
    if module.has_changed is False:
        module.exit_msg = 'No change in OSPFv3 global config'
    module.exit_json(msg=module.exit_msg, changed=module.has_changed)


def check_ip_addr_show(module):
    cmd_line = "/sbin/ip addr show %s" % (module.params.get('interface'))
    result = run_cl_cmd(module, cmd_line)
    for _line in result:
        m0 = re.match('\s+inet6\s+\w+', _line)
        if m0:
            return True
    return False


def get_interface_addr_config(module):
    ifacename = module.params.get('interface')
    cmd_line = "/sbin/ifquery --format json %s" % (ifacename)
    int_config = run_cl_cmd(module, cmd_line, True, False)
    ifquery_obj = json.loads(int_config)[0]
    iface_has_address = False
    if 'address' in ifquery_obj.get('config'):
        for addr in ifquery_obj.get('config').get('address'):
            try:
                socket.inet_aton(addr.split('/')[0])
                iface_has_address = True
                break
            except socket.error:
                pass
    else:
        iface_has_address = check_ip_addr_show(module)
        if iface_has_address is False:
            _msg = "interface %s does not have an IPv6 address configured. " +\
                "Required for OSPFv3 to work"
            module.fail_json(msg=_msg)
    # for test purposes only
    return iface_has_address


def enable_or_disable_ospf_on_int(module):
    ifacename = module.params.get('interface')
    _state = module.params.get('state')
    iface_config = module.interface_config.get(ifacename)
    if iface_config is None:
        _msg = "%s is not found in Quagga config. " % (ifacename) + \
            "Check that %s is active in kernel" % (ifacename)
        module.fail_json(msg=_msg)
        return False  # for test purposes
    found_area = None
    for i in iface_config:
        m0 = re.match('area\s+([0-9.]+)', i)
        if m0:
            found_area = m0.group(1)
            break
    if _state == 'absent':
        for i in iface_config:
            if found_area:
                cmd_line = '/usr/bin/cl-ospf6 clear %s area' % \
                    (ifacename)
                run_cl_cmd(module, cmd_line)
                module.has_changed = True
                module.exit_msg += "OSPFv3 now disabled on %s " % (ifacename)
        return False
    area_id = module.params.get('area')
    if found_area != area_id:
        cmd_line = '/usr/bin/cl-ospf6 interface set %s area %s' % \
            (ifacename, area_id)
        run_cl_cmd(module, cmd_line)
        module.has_changed = True
        module.exit_msg += "OSPFv3 now enabled on %s area %s " % \
            (ifacename, area_id)
    return True


def update_point2point(module):
    ifacename = module.params.get('interface')
    point2point = module.params.get('point2point')
    iface_config = module.interface_config.get(ifacename)
    found_point2point = None
    for i in iface_config:
        m0 = re.search('ipv6\s+ospf\s+network\s+point-to-point', i)
        if m0:
            found_point2point = True
            break
    if point2point:
        if not found_point2point:
            cmd_line = '/usr/bin/cl-ospf6 interface set %s network point-to-point' % \
                (ifacename)
            run_cl_cmd(module, cmd_line)
            module.has_changed = True
            module.exit_msg += 'OSPFv3 point2point set on %s ' % (ifacename)
    else:
        if found_point2point:
            cmd_line = '/usr/bin/cl-ospf6 interface clear %s network' % \
                (ifacename)
            run_cl_cmd(module, cmd_line)
            module.has_changed = True
            module.exit_msg += 'OSPFv3 point2point removed on %s ' % \
                (ifacename)


def update_passive(module):
    ifacename = module.params.get('interface')
    passive = module.params.get('passive')
    iface_config = module.interface_config.get(ifacename)
    found_passive = None
    for i in iface_config:
        m0 = re.search('passive-interface', i)
        if m0:
            found_passive = True
            break
    if passive:
        if not found_passive:
            cmd_line = '/usr/bin/cl-ospf6 interface set %s passive' % \
                (ifacename)
            run_cl_cmd(module, cmd_line)
            module.has_changed = True
            module.exit_msg += '%s is now OSPFv3 passive ' % (ifacename)
    else:
        if found_passive:
            cmd_line = '/usr/bin/cl-ospf6 interface clear %s passive' % \
                (ifacename)
            run_cl_cmd(module, cmd_line)
            module.has_changed = True
            module.exit_msg += '%s is no longer OSPFv3 passive ' % \
                (ifacename)


def config_ospf_interface_config(module):
    enable_int_defaults(module)
    module.has_changed = False
    # get all ospf related config from quagga both globally and iface based
    get_running_config(module)
    # if interface does not have ipv4 address module should fail
    get_interface_addr_config(module)
    # if ospf should be enabled, continue to check for the remaining attrs
    if enable_or_disable_ospf_on_int(module):
        # update ospf point-to-point setting if needed
        update_point2point(module)
        # update ospf interface passive setting
        update_passive(module)


def saveconfig(module):
    if module.params.get('saveconfig') is True and\
            module.has_changed:
        run_cl_cmd(module, '/usr/bin/vtysh -c "wr mem"')
        module.exit_msg += 'Saving Config '


def enable_int_defaults(module):
    if not module.params.get('area'):
        module.params['area'] = '0.0.0.0'
    if not module.params.get('state'):
        module.params['state'] = 'present'


def check_if_ospf_is_running(module):
    if not os.path.exists('/var/run/quagga/ospf6d.pid'):
        _msg = 'OSPFv3 process is not running. Unable to execute command'
        module.fail_json(msg=_msg)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            router_id=dict(type='str'),
            interface=dict(type='str'),
            area=dict(type='str'),
            state=dict(type='str',
                       choices=['present', 'absent']),
            point2point=dict(type='bool', choices=BOOLEANS),
            saveconfig=dict(type='bool', choices=BOOLEANS, default=False),
            passive=dict(type='bool', choices=BOOLEANS)
        ),
        mutually_exclusive=[['interface'],
                            ['router_id', 'interface']]
    )
    check_if_ospf_is_running(module)

    check_dsl_dependencies(module, ['state', 'area',
                                    'point2point', 'passive'],
                           'interface', 'swp1')
    module.has_changed = False
    module.exit_msg = ''
    if has_interface_config(module):
        config_ospf_interface_config(module)
    else:
        # Set area to none before applying global config
        module.params['area'] = None
        add_global_ospf_config(module)
    saveconfig(module)
    if module.has_changed:
        module.exit_json(msg=module.exit_msg, changed=module.has_changed)
    else:
        module.exit_json(msg='no change', changed=False)

# import module snippets
from ansible.module_utils.basic import *
import re
import os
import socket
# incompatible with ansible 1.4.4 - ubuntu 12.04 version
# from ansible.module_utils.urls import *


if __name__ == '__main__':
    main()

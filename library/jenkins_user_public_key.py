#!/usr/bin/python
""" see DOCUMENTATION """
from ansible.module_utils.basic import AnsibleModule
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

DOCUMENTATION = '''
---
module: jenkins_user_public_key
short_description: Sets up the root ssh public key into the admin jenkins user
'''

def main():
    """ Main function """
    module = AnsibleModule(
        argument_spec={
            "jenkins_home": {"type": "str"},
            "username": {"type": "str"}
        }
    )

    xml_file_name = "%s/users/%s/config.xml" % (module.params['jenkins_home'], module.params['username'])
    changed = set_pub_key(xml_file_name)
    module.exit_json(changed=changed)

def set_pub_key(xml_file_name):
    with open('/root/.ssh/id_rsa.pub') as public_key_file:
        public_key = public_key_file.read()

    tree = ET.parse(xml_file_name)
    root = tree.getroot()
    properties = root.find('properties')
    ssh_properties = properties.find('org.jenkinsci.main.modules.cli.auth.ssh.UserPropertyImpl')
    if ssh_properties is None:
        ssh_properties = ET.SubElement(properties, 'org.jenkinsci.main.modules.cli.auth.ssh.UserPropertyImpl')

    authorized_keys = ssh_properties.find('authorizedKeys')
    if authorized_keys is None:
        authorized_keys = ET.SubElement(ssh_properties, 'authorizedKeys')

    if authorized_keys.text != public_key:
        authorized_keys.text = public_key
        tree.write(open(xml_file_name, 'wb'))
        changed = True
    else:
        changed = False

    return changed

if __name__ == '__main__':
    main()

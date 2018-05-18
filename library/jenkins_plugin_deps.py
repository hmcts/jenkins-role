#!/usr/bin/python
""" see DOCUMENTATION """
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: jenkins_plugin_deps
short_description: Finds deps for Jenkins plugins
description: Takes a list of desired Jenkins plugins, and an object json decoded 'plugins' section of /var/lib/jenkins/updates/default.json. Will go through the desired plugins and find all nested dependencies. Outputs a final list of plugins to install
'''

EXAMPLES = '''
- jenkins_plugin_deps:
    plugins:
      - "greenballs"
      - "github"
    jenkins_updates_file_plugins: present
  register: plugin_deps_output
- debug:
    var: plugin_deps_output.plugins_and_deps
'''

def main():
    """ Main function """
    module = AnsibleModule(
        argument_spec={
            "plugins": {"type": "list"},
            "jenkins_updates_file_plugins": {"type": "dict"}
        }
    )

    # make the output list, starting with just the plugins that were requested
    plugins_and_deps = module.params['plugins']

    # Loop through the list of plugins (and dependecies once we find some),
    # add any new dependecies we find, and keep looping to get their subsequent dependencies too
    loop_again = True
    while loop_again:
        loop_again = False
        for plugin in plugins_and_deps:
            if plugin in module.params['jenkins_updates_file_plugins']:
                for dep in module.params['jenkins_updates_file_plugins'][plugin]['dependencies']:
                    if dep['name'] not in plugins_and_deps:
                        plugins_and_deps.append(dep['name'])
                        loop_again = True
            else:
                # plugin wasn't in the list of updates
                pass

    # sort and deduplicate plugins_and_deps
    plugins_and_deps = sorted(list(set(plugins_and_deps)))

    module.exit_json(changed=False, plugins_and_deps=plugins_and_deps)

if __name__ == '__main__':
    main()

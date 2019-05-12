#!/bin/bash

# launch three instances(VMs) on NeCTAR
#. ./unimelb-comp90024-group-62-openrc.sh; ansible-playbook --ask-become-pass ./launchVMs/playbook.yaml

# format inventory file /deployVMs/hosts
#ansible-playbook ./launchVMs/formatHosts.yaml

#ansible-playbook -i ./deployVMs/hosts ./deployVMs/playbooks/proxy.yaml
#ansible-playbook -i ./deployVMs/hosts ./deployVMs/playbooks/volume.yaml
#ansible-playbook -i ./deployVMs/hosts ./deployVMs/playbooks/couchdb.yaml
#ansible-playbook -i ./deployVMs/hosts ./deployVMs/playbooks/harvester.yaml
#ansible-playbook -i ./deployVMs/hosts ./deployVMs/playbooks/analyser.yaml
#ansible-playbook -i ./deployVMs/hosts ./deployVMs/playbooks/webserver.yaml



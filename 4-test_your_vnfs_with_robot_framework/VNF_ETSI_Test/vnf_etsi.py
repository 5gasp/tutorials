'''
5GASP- VNFD Validation Test
@author: Adrian-Cristian (Chris) Nicolaescu <chris.nicolaescu@bristol.ac.uk> 
'''
import json
import os
import pip
import importlib.util

os.system("./variables.txt")
host = os.getenv('OSM_ip')
username = os.getenv('machine_username')
password = os.getenv('machine_password')

OSM_user = os.getenv('OSM_username')
OSM_pass = os.getenv('OSM_password')
OSM_project = os.getenv('OSM_project')

vnf = os.getenv('VNF_name')

# vim = os.getenv('VIM_name')




packages = ['paramiko','robotframework']
for package in packages:
    if (spec := importlib.util.find_spec(package)) is  None:
        pip.main(['install', package])       
    
import paramiko

#test
def vnf_etsi():
    machine = paramiko.SSHClient()
    machine.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        machine.connect(hostname=host, username=username, password=password)
    except:
        print("[!] Cannot connect to the SSH Server")
        exit()

    # Executing VNFD validation commands
    stdin, stdout, stderr = machine.exec_command(f"cd /home/ubuntu/Backup\ VM/;pwd")
    err = str(stderr.read(), "utf-8")
    print(f"{err=}")
    stdin, stdout, stderr = machine.exec_command(f"pwd")
    curr = str(stdout.read(), "utf-8")
    print(f"{curr=}")
    # if knf:
    #     stdin, stdout, stderr = machine.exec_command(f"osm --user 5gasp_univbris --password 5GASPUNiVBRI$ --project 5GASP_UNIVBRIS ns-create --ns_name {knf}_knf --nsd_name {knf}_nsd --vim_account {vim}")
    # else:
    stdin, stdout, stderr = machine.exec_command(f"cd /home/ubuntu/Backup\ VM/;osm --user {OSM_user} --password {OSM_pass} --project {OSM_project} package-validate {vnf}")
    print(f"{stdin=}")
    print(f"{stdout=}")
    print(f"{stderr=}")
    valResult = str(stdout.read(), "utf-8")
    if "OK" in valResult:
        vnf_val = 'OK'
    else:
        vnf_val = 'ERROR'
    print(f"{vnf_val=}")
    # valResult = stdout.channel.recv_exit_status().read().decode()
    # obj = json.loads(valResult)
    try:
        # vnf_val = valResult
        print(f"VNF (hash): {valResult}")
    except:
        return "Not found"
    return vnf_val


if __name__ == '__main__':
    vnf_etsi()
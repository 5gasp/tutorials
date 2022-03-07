'''
5GASP- Jitter Test
@author: Daniel Gomes <dagomes@av.it.pt> & Pedro Bastos <pedro.bas@av.it.pt> 
'''
import json
import os
import pip
import importlib.util

host1 = os.getenv('jitter_host1_ip')
username1 = os.getenv('jitter_host1_username')
password1 = os.getenv('jitter_host1_password')

host2 = os.getenv('jitter_host2_ip')
username2 = os.getenv('jitter_host2_username')
password2 = os.getenv('jitter_host2_password')



packages = ['paramiko','robotframework']
for package in packages:
    if (spec := importlib.util.find_spec(package)) is  None:
        pip.main(['install', package])       
    
import paramiko

#test
def jitter():
    machine1 = paramiko.SSHClient()
    machine1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    machine2 = paramiko.SSHClient()
    machine2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        machine1.connect(hostname=host1, username=username1, password=password1)
        machine2.connect(hostname=host2, username=username2, password=password2)
    except:
        print("[!] Cannot connect to the SSH Server")
        exit()

    # Executing iPerf commands
    machine1.exec_command("iperf3 -s -1")
    stdin, stdout, stderr = machine2.exec_command(f"iperf3 -c {host1} -u --json -t 5")
    iperfResult = stdout.read().decode()
    obj = json.loads(iperfResult)
    try:
        jitter_ms = float(obj['end']['sum']['jitter_ms'])
        print(f"Jitter: {jitter_ms}")
    except:
        return "Not found"
    return jitter_ms


if __name__ == '__main__':
    jitter()
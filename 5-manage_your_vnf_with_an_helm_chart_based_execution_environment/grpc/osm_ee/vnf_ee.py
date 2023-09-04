# @Author: Daniel Gomes
# @Date:   2023-02-03 09:27:39
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2023-02-16 09:42:53
import os
import logging
import yaml
import json
import asyncio
from osm_ee.exceptions import VnfException
import osm_ee.utils as utils

CONFIG_FILE_NAMES = ('time_window', 'number_versions')
PLAYBOOK_PATH = "/app/EE/osm_ee/vnf"
SSH_KEY_FILE = "~/.ssh/id_rsa"

class VnfEE:
    def __init__(self, config_params):
        self.logger = logging.getLogger('osm_ee.vnf')
        self.config_params = config_params

        #self.config_path = os.getenv('CONFIG_PATH', default='/config')

    
    async def config(self, id, params):
        debug_params = { k:v for k,v in params.items() if k != "ssh-password"}
        self.logger.debug("Execute action config params: {}".format(debug_params))
        # Config action is special, params are merged with previous config calls
        self.config_params.update(params)
        yield "OK", "Configured"

    async def sleep(self, id, params):
        self.logger.debug("Execute action sleep, params: {}".format(params))

        for i in range(3):
            await asyncio.sleep(5)
            self.logger.debug("Temporal result return, params: {}".format(params))
            yield "PROCESSING", f"Processing {i} action id {id}"
        yield "OK", f"Processed action id {id}"

    async def ansible_playbook(self, id, params):
        self.logger.debug("Execute action ansible_playbook, params: '{}'".format(params))

        try:
            self._check_required_params(params, ["playbook-name"])
            params["ansible_user"] = self.config_params["ssh-username"]
            inventory = self.config_params["ssh-hostname"] + ","
            has_terminator = str(params['playbook-name']).endswith('.yaml')

            playbook_name = params['playbook-name']
            if not has_terminator:
                playbook_name = f"{params['playbook-name']}.yaml"
                
            playbook = f"{PLAYBOOK_PATH}/{playbook_name}"
            self.logger.debug(f"playbook {playbook}")

            #os.environ["ANSIBLE_HOST_KEY_CHECKING"] = "False"
            os.environ["ANSIBLE_STDOUT_CALLBACK"] = "json"
            self.logger.debug(f"inventory {inventory} params {params}")
            return_code, stdout, stderr = await utils.execute_playbook(
                playbook, inventory, params)
            stdout = self._parse_json_playbook_output(stdout).encode()
            status = "OK" if return_code == 0 else "ERROR"

            yield status, stdout + stderr
        except Exception as e:
            self.logger.debug("Error executing ansible playbook: {}".format(repr(e)))
            yield "ERROR", str(e)


    @staticmethod
    def _check_required_params(params, required_params):
        for required_param in required_params:
            if required_param not in params:
                raise VnfException("Missing required param: {}".format(required_param))


    @staticmethod
    def _parse_json_playbook_output(output)-> str:
        data = json.loads(output) 

        res = {'plays': []}
        for k in data['plays']:
        
            # wont work for nested tasks...
            for task in k['tasks']:
                if task['task']['name'] == 'Gathering Facts':
                    del task['hosts']
            res['plays'].append(k)
        res['stats'] = data['stats']
        return json.dumps(res)
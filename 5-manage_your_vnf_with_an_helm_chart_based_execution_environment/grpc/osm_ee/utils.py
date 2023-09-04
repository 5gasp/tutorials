# @Author: Daniel Gomes
# @Date:   2023-02-15 15:28:05
# @Email:  dagomes@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2023-02-15 16:34:31
##
# Copyright 2019 Telefonica Investigacion y Desarrollo, S.A.U.
# This file is part of OSM
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For those usages not covered by the Apache License, Version 2.0 please
# contact with: nfvlabs@tid.es
##

import logging
import asyncio
from shlex import split, quote
import json
import os

logger = logging.getLogger("osm_ee.utils")
 

SSH_KEY_FILE = "~/.ssh/id_rsa"


async def local_async_exec(command: str
                           ) -> (int, str, str):
    """
        Executed a local command using asyncio.
        TODO - do not know yet if return error code, and stdout and strerr or just one of them
    """
    scommand = split(command)

    logger.debug("Execute local command: {}".format(command))
    process = await asyncio.create_subprocess_exec(
        *scommand,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    # wait for command terminate
    stdout, stderr = await process.communicate()

    return_code = process.returncode
    logger.debug("Return code: {}".format(return_code))

    output = ""
    if stdout:
        output = stdout.decode()
        logger.debug("Output: {}".format(output))

    if stderr:
        out_err = stderr.decode()
        logger.debug("Stderr: {}".format(out_err))

    return return_code, stdout, stderr

async def add_host(target_ip):
    known_hosts_path = os.path.expanduser("~/.ssh/known_hosts")

    # Construct the command
    command = f"ssh-keyscan -H {target_ip}"
    return_code, stdout, stderr = await local_async_exec(command)
    
    with open(known_hosts_path, "a") as known_hosts_file:
        known_hosts_file.write(stdout.decode())
        return return_code, stdout, stderr

async def execute_playbook(playbook_name: str, inventory: str,
                           extra_vars: dict,
                           ):

    command = 'ansible-playbook --inventory={} --private-key={} --extra-vars {} {}'.format(
               quote(inventory),
               quote(SSH_KEY_FILE),
               quote(json.dumps(extra_vars)),
               quote(playbook_name))

    logger.debug("Command to be executed: {}".format(command))
    return_code, stdout, stderr = await local_async_exec(command)
    logger.debug("Return code: {}".format(return_code))
    logger.debug("stdout: {}".format(stdout))
    logger.debug("stderr: {}".format(stderr))

    return return_code, stdout, stderr

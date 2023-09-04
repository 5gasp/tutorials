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

import sys
import yaml
import asyncio
import uuid
import socket

from grpclib.client import Channel

from frontend_pb2 import PrimitiveRequest
from frontend_pb2 import SshKeyRequest, SshKeyReply
from frontend_grpc import FrontendExecutorStub


async def frontend_client(host_name, port, primitive_name, params):

    ip_addr = socket.gethostbyname(host_name)
    channel = Channel(ip_addr, port)
    try:
        stub = FrontendExecutorStub(channel)

        if (primitive_name == "get_ssh_key"):
            print("Get ssh key")
            reply: SshKeyReply = await stub.GetSshKey(SshKeyRequest())
            print(reply.message)
        else:
            async with stub.RunPrimitive.open() as stream:
                primitive_id = str(uuid.uuid1())
                print("Execute primitive {}, params: {}".format(primitive_name, params))
                await stream.send_message(
                    PrimitiveRequest(id=primitive_id, name=primitive_name, params=yaml.dump(params)), end=True)
                async for reply in stream:
                    print(reply)
                #replies = [reply async for reply in stream]
                #print(replies)
    except Exception as e:
        print("Error executing primitive {}: {}".format(primitive_name, str(e)))
        #print(traceback.format_exc())
    finally:
        channel.close()


if __name__ == '__main__':

    args = sys.argv[1:]
    if (len(args) < 1):
        print("Usage: host port primitive_name params")
    else:
        host_name = args[0]
        port = args[1]
        primitive_name = args[2]
        arg_params = args[3] if len(args) >= 4 else ""
        print(primitive_name)
        print(arg_params)
        params = yaml.safe_load(arg_params)

        loop = asyncio.get_event_loop()
        try:
            task = asyncio.ensure_future(frontend_client(host_name, port, primitive_name, params))
            loop.run_until_complete(task)
        finally:
            loop.close()

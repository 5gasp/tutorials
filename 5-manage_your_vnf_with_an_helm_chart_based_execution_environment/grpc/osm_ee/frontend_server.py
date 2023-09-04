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

import asyncio
import logging
import os

from grpclib.utils import graceful_exit
from grpclib.server import Server, Stream

from osm_ee.frontend_grpc import FrontendExecutorBase
from osm_ee.frontend_pb2 import PrimitiveRequest, PrimitiveReply
from osm_ee.frontend_pb2 import SshKeyRequest, SshKeyReply

from osm_ee.base_ee import BaseEE
import osm_ee.utils as util_ee


class FrontendExecutor(FrontendExecutorBase):

    def __init__(self):
        self.logger = logging.getLogger('osm_ee.frontend_server')
        self.base_ee = BaseEE()

    async def RunPrimitive(self, stream: Stream[PrimitiveRequest, PrimitiveReply]) -> None:
        request = await stream.recv_message()
        try:
            self.logger.debug(f'Run primitive: id {request.id}, name: {request.name}, params: {request.params}')
            async for status, detailed_message in self.base_ee.run_action(request.id, request.name, request.params):
                self.logger.debug(f'Send response {status}, {detailed_message}')
                await stream.send_message(
                    PrimitiveReply(status=status, detailed_message=detailed_message))
        except Exception as e:
            self.logger.debug(f'Error executing primitive: id {request.id}, name: {request.name}, error_msg: {str(e)}')
            await stream.send_message(
                PrimitiveReply(status="ERROR", detailed_message=str(e)))

    async def GetSshKey(self, stream: Stream[SshKeyRequest, SshKeyReply]) -> None:
        request = await stream.recv_message()
        assert request is not None
        self.logger.debug("receving request for ssh key")
        message = await self.base_ee.get_ssh_key()
        await stream.send_message(SshKeyReply(message=message))


async def main(*, host: str = '0.0.0.0', port: int = 8001) -> None:
    logging.basicConfig()
    logger = logging.getLogger('osm_ee')
    logger.setLevel(logging.DEBUG)

    # Generate ssh key
    # file_dir = os.path.expanduser("~/.ssh/id_rsa")
    # command = "ssh-keygen -q -t rsa -N '' -f {}".format(file_dir)
    # return_code, stdout, stderr = await util_ee.local_async_exec(command)
    # logger.debug("Generated ssh_key, return_code: {}".format(return_code))

    # Start server
    server = Server([FrontendExecutor()])
    with graceful_exit([server]):
        await server.start(host, port)
        logging.getLogger('osm_ee.frontend_server').debug(f'Serving on {host}:{port}')
        await server.wait_closed()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        main_task = asyncio.ensure_future(main())
        loop.run_until_complete(main_task)
    finally:
        loop.close()

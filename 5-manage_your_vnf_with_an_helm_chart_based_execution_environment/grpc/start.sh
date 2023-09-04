#!/bin/bash
# @Author: Daniel Gomes
# @Date:   2023-02-15 15:28:05
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2023-02-15 16:49:59
#!/bin/bash
##
# Copyright 2015 Telefonica Investigacion y Desarrollo, S.A.U.
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
##

# This script is intended for launching RO from a docker container.
# It waits for mysql server ready, normally running on a separate container, ...
# then it checks if database is present and creates it if needed.
# Finally it launches RO server.
EE_PATH=/app/EE

# Install vnf vendor additional required libraries
echo "Install additional libraries"
bash ${EE_PATH}/osm_ee/vnf/install.sh



# Start frontend
echo "Starting frontend server"
python3 -m osm_ee.frontend_server

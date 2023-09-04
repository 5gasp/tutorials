#  How to manage your VNF with an Helm Chart-based Execution Environment (EE)

## Introduction to Execution Environments in OSM

OSM's Execution Environments (EE) provide a runtime framework to run day-1 and day-2 primitives. These EE provide the means for NF-specific management code to run it into a dedicated helm chart, which is deployed into OSM's system cluster. From there, the EE interacts with the managed NF (e.g. via SSH), providing a NF-agnostic mean to manage NFs by OSM.

OSM communicates with its EE to trigger actions via gRPC calls, which are handled by a fronted component (running in a pod) in its constituent helm chart. In order to ease the NF onboarding tasks, there is already a helm chart template available including:
-  a frontend element which implements the gRPC interface required by OSM (exposed via a Kubernetes service). **However the OSM's current frontend element is outdated ( due to GRPC), thus a custom one will be used **
-  and an optional back-end, in charge of the interaction with the NF.

## Software Installation

Installation of Helm
```
$ curl https://get.helm.sh/helm-v3.11.2-linux-amd64.tar.gz
$ tar -zxvf helm-v3.11.2-linux-amd64.tar.gz
$ mv linux-amd64/helm /usr/local/bin/helm
```

Installation of Ansible
```
pip3 install ansible
```


## Code Structure
Inside this directory you may find three core subdirectories:

 -  `grpc`(Includes the underlying code of the frontend element which implements the gRPC interface)
 -  `simple_ee_vnf` (Includes the VNFD and Helm Chart)
 -  `simple_ee_ns` (Includes the NSD)
 
 The `completed` folder, contains the resolution of the tutorial.
## gRPC image

The code used has been adapted from OSM'S. Thus, you should build the Docker image and push it to your Images Registry.

If the OSM's gRPC code is not up to date with Protoc Buffers, to regenerate the protocol buffers do the following:

Download and install the python compiler from [ProtoBuf](https://github.com/protocolbuffers/protobuf/releases) following the instructions in the README file.

Delete `frontend_pb2.py` and `frontend_grpc.py`.

Run the compiler: 

`protoc -I=/path/to/grpc/osm_ee/ --python\_out=/path/to/grpc/osm_ee/ /path/to/grpc/osm_ee/frontend.proto`

Once, this is done you may build the Docker image and upload it to your registry using the following commands:

```
docker build -t  <your_registry_domain_name>/<the_grpc_image_name> .
docker push  <your_registry_domain_name>/<the_grpc_image_name>
```

# Creating day-1/day-2 primitives via Ansible
All your Ansible playbooks must be present in your Helm chart inside the `source` folder (`/simple_ee_vnf/helm-charts/eechart/source`). In the `source` folder there are already two empty files called `playbook.yaml` and `update_file.yaml`. 

Inside the `playbook.yaml` file on the source `directory` introduce the following code, which perform a day1 operation responsible for creating an empty file on the VNF's VM.

```yaml
- hosts: all
  name: Create an empty file on the remote machine
  become: true
  tasks:
  - name: Create an empty file on the remote machine
    file:
      path: "/home/ubuntu/myfile.txt"
      state: touch
```

Then, introduce the following code block to the empty playbook `update_file,yaml` on the source `directory`. This is the playbook to be invoked on the day-2 primitive. This primitive will update the file's content with the user input. The workflow will be explained with further detail. 

```yaml
- hosts: all
  vars:
    content: "{{ params.content }}"
  tasks:
  - name: Update the content of the file
    blockinfile:
      path: "/home/ubuntu/myfile.txt"
      block: |
       "{{content}}"
```

### Change the Helm Chart Content

Inside the Helm Chart you may find the file `values.yaml` which will be used to change variable names, such as the image names used. You should change to include the GRPC image that OSM needs to interact.
For instance:

```yaml
name: ansible-grpc
repository: atnog-harbor.av.it.pt/5gasp/ansible-grpc-keyauth@sha256
tag: 28e4a0a5cb210cabbc39d4b4fb597e786975d65e7a3a54365b1915b30fd72bbf
pullPolicy: Always
```

In OSM 14, the Helm-Charts are deployed in a namespace created on-the-fly. However, we cannot share Secrets across namespaces, thus one solution can be to include the Image Pull Secret inside the Helm Chart.
To that end, on the same file, `values.yaml`, make sure to edit the key `dockerConfig`'s value to access your Images Registry



## Change the VNFD
A pre-requirement to define EE-based primitives is including the appropriate reference in the descriptor to the own EE, and then a reference to the corresponding day-1 and day-2 primitives that are hosted in the EE. You may find the VNFD in the root of the VNF artifact folder (`simple_ee_vnf/sample_ee_vnfd.yaml`)
The first is achieved by adding an execution-environment-list block, where one or more EEs (there might be more than one) are indicated. Inside the `df` element put the following excerpt of code, aligned with the same identation level as `vdu-profile`:

```yaml
lcm-operations-configuration:
      operate-vnf-op-config:
        day1-2:
        - execution-environment-list:
          - external-connection-point-ref: vnf-mgmt-ext
            helm-chart: eechart
            helm-version: v3
            id: sample
          id: simple
          config-access:
            ssh-access:
              default-user: ubuntu
              required: true
          initial-config-primitive:
          - execution-environment-ref: sample
            name: config
            parameter:
            - name: ssh-hostname
              value: <rw_mgmt_ip>
            - name: ssh-username
              value: ubuntu
            - name: ssh-password
              value: password
            seq: 1
```
The next step is to include the day1-primitive block referencing the `playbook.yaml` file, inside the `initial-config-primitive block`. The parameter's value must match the playbook's file name.

```yaml
- execution-environment-ref: sample
  name: ansible_playbook
  parameter:
    - name: playbook-name
      value: playbook
  seq: 2
```
 In this tutorial, as mentioned, we will create a day-2 primitive. The primitive requires two parameters: the playbook file name (in the provided example, playbook-name) as well as the content to add to the file created on day-1 operation (content). Make sure to add the following block code bellow `initial-config-primitive`directive :
 
```yaml
config-primitive:
- execution-environment-primitive: ansible_playbook
  execution-environment-ref: sample
  name: ansible_playbook
  parameter:
    - data-type: STRING
      name: playbook-name
    - data-type: STRING
      name: content
      default-value: <content>
```


## Change the  NSD
Regarding the NSD ( `simple_ee_ns/nsd.yaml`) you should change the `vim-network-name` to the name of your VIM Network

```yaml
 virtual-link-desc:
    - id: mgmtnet
      mgmt-network: true
      vim-network-name: XXXXX
```


## Upload the NFV Artifacts

To upload the NS and VNF packages you may run the following commands:

```bash
osm nfpkg-create simple_ee_vnf
osm nspkg-create simple_ee_ns
```

## Instantiate the NS
Now, we are ready to deploy the VNF. Using the OSM CLI you may use the following command:

`osm ns-create --ns_name 5gasp_ee_tutorial --nsd_name simple_ee-ns --vim_account <your_vim_account>`

To check if the day-1 operations has succeeded, in another terminal tab, we can now enter into the machine via SSH:

```
ssh ubuntu@<your_vm_ip>
```

By doing a simple `ls` command we can verify that the file has been created:

```bash
$ ls
myfile.txt
```

## Performing the day-2 operation
To perform the day-2 operation we have can run the following command:
```
 osm ns-action  --vnf_name simple --vdu_id mgmtVM  --action_name ansible_playbook --params "{\"playbook-name\": \"update_file\", \"content\": \"Hello World!\"}"   5gasp_ee_tutorial
 ``` 
In the VNF's VM we can verify that the content of the file has been updated:
 
```bash
$ cat myfile.txt

# BEGIN ANSIBLE MANAGED BLOCK
"Hello"
# END ANSIBLE MANAGED BLOCK
```









# From Helm Chart to CNF tutorial

## What is a CNF?

A Cloud-native Network Function (CNF) is a software-based network function designed to operate in cloud-native environments, such as Kubernetes clusters or container orchestration platforms. CNFs are a fundamental component of modern telecommunications and networking systems, enabling greater flexibility, scalability, and agility compared to traditional hardware-based network functions.

Key Characteristics of CNFs:

* Software-Defined - CNFs are entirely software-defined, which means they are implemented as software applications or microservices rather than relying on dedicated hardware.

* Containerization - CNFs are often containerized, allowing them to run in lightweight, isolated containers that can be easily orchestrated and scaled using container orchestration tools like Kubernetes.

* Scalability - CNFs can be dynamically scaled up or down to meet varying network traffic demands, ensuring efficient resource utilization.

* Microservices Architecture - CNFs are typically designed using a microservices architecture, where individual functions are decoupled and can be independently developed, deployed, and scaled.

## How does a CNF work in the context of OSM?

In the context of Open Source MANO (OSM), a CNF works as part of a larger network service orchestration and management framework. Here's how a CNF typically works within the OSM framework:

* Descriptor Creation - Network service providers or administrators define the network service requirements using OSM descriptors. These descriptors describe the service's topology, including CNFs, virtual links, and other resources.

* Onboarding CNFs - CNFs, packaged as container images, are onboarded into the OSM platform. The onboarding process involves registering the CNF images and creating the necessary descriptors that define how these CNFs should be deployed and configured.

* Descriptor Instantiation - When a network service is requested, OSM uses the descriptors to instantiate the service. This involves deploying CNFs as containers in the cloud-native infrastructure (e.g., Kubernetes clusters) according to the specifications defined in the descriptors.

* Service Orchestration - OSM orchestrates the CNFs and other network resources, ensuring that the CNFs are properly configured and connected to form the desired network service. OSM handles aspects like scaling, load balancing, and network connectivity.

* Lifecycle Management - OSM manages the entire lifecycle of CNFs within the network service. This includes:

  1. Instantiation - Deploying CNFs when a service is created.
  2. Scaling - Automatically adjusting the number of CNF instances based on demand.
  3. Monitoring - Collecting performance metrics and logs from CNFs.
  4. Healing - Automatically recovering from CNF failures by restarting or replacing instances.
  5. Termination - Gracefully decommissioning CNFs when they are no longer needed.

* Service Assurance and Scaling - OSM continuously monitors the CNFs and the network service's performance. If traffic patterns change or issues arise, OSM can trigger the scaling of CNFs to accommodate increased traffic or to maintain service quality.

* Service Termination - When a network service is no longer required, OSM handles the termination of CNFs and associated resources. This ensures efficient resource utilization.

Overall, a CNF in the context of OSM benefits from the orchestration, management, and scaling capabilities provided by the OSM platform. This integration simplifies the deployment and lifecycle management of CNFs within network services and contributes to the flexibility and agility of modern networking systems.

## Packing your Helm Chart

For this tutorial, we will use a custom Helm Chart with the NEF Emulator. It should be mentioned that you should only use this Chart, in an development environment. For instance, no volumes are being used, which makes the stored data volatile.
First, lets encapsulate the Helm Chart in `.tgz` archive. For this intent, execute the following command:

```bash
$ helm package nef-emulator
Successfully packaged chart and saved it to: /home/user/from-helm-chart-to-cnf-tutorial/nef-emulator-0.1.0.tgz
```
Now you should be able to see the package `nef-emulator-0.1.0.tgz`:

```bash
$ ls | grep nef-emulator-0.1.0.tgz
nef-emulator-0.1.0.tgz

```

## Updating your VNF Artifact
For this tutorial, we will not rely on Helm Chart Repositories. Instead, we will indicate on the VNF Descriptor to use a local helm chart artifact. The following excerpt of code has been tailored for OSM 13 versions or lower. Concerning OSM 14, to the best of our knowledge, it is not possible to onboard a VNF Artifact that containing a local Helm Chart Artifact.
Introduce this excerpt of code on your VNFD (`./vnf/vnfd.yaml`), below the `id` key, with the same level of identation. Make sure to replace, the `id` of your k8s_cluster, by the one you are using on OSM. On the other hand, the value of the `helm-chart` key, must match the name of the Helm Chart artifact to be used.

```yaml
  k8s-cluster:
    nets:
    - id: mgmtnet
  kdu:
  - name: nef-emulator
    helm-chart: "nef-emulator-0.1.0.tgz"
    helm-version: v3
```

Now, we shall place the Helm Chart archive inside the VNF Artifact. To do so, first we must create a directory with the name `helm-chart-v3s`. This will instruct OSM too look for a local helm chart, with the name indicated on the VNFD:

```bash
$ cd vnf
$ mkdir helm-chart-v3s
$ cp ../nef-emulator-0.1.0.tgz ./helm-chart-v3s/
```
## Updating your NSD

Regarding your NSD, you will only require to update the `vim-network-name` (`./ns/nsd.yaml`), to match the one you are using on your OSM instance.

```yaml
virtual-link-desc:
    -   id: mgmtnet
        mgmt-network: 'true'
        vim-network-name: new_5gasp   
```

# NFV Artifacts Onboarding and Instantiation
Carrying on, we can now onboard into OSM the VNF and NSD packages created:

```bash
$ osm nfpkg-create vnf
$ osm nspkg-create ns
```
To instantiate the CNF, you may simply use the following command. Make sure to replace the VIM account to match the one used in your osm
```bash
$ osm ns-create --ns_name cnf-tutorial --nsd_name nef_emulator_nsd --vim_account <your_vim_account>
```



# Checking the status of the CNF

To check if the CNF's services have been created with success, you shall enter inside your Kubernetes Cluster and check if there are any pods related to the NEF Emulator. For that, execute the following command, inside the Cluster's Machine:

```bash
$ kubectl get pods -A | grep nef

15d723ae-b926-4465-9e61-5d72729c06a4   nef-emulator-0-1-0-tgz-0096146112-db-0                       1/1     Running   0 
15d723ae-b926-4465-9e61-5d72729c06a4   nef-emulator-0-1-0-tgz-0096146112-mongo-0                    1/1     Running   0 
15d723ae-b926-4465-9e61-5d72729c06a4   nef-emulator-0-1-0-tgz-0096146112-report-69d5c46796-6ms2b    1/1     Running   0 
15d723ae-b926-4465-9e61-5d72729c06a4   nef-emulator-0-1-0-tgz-0096146112-backend-595fd4c777-74tfw   1/1     Running   0 
```



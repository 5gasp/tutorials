# Learning Path in the 5GASP Community

#### This is a ultimate guide to fully understand what each tutorial means and how to do the full learning path.

## Initial requirements 

Before going through our set of tutorials, you should make sure that you have the technological background first. 

As a NetApp developer, you should have:

* Basic knowledge in the matter;
* What is a VNF and how does it work, as well as VIMs and NS;
* Basic knowledge on OSM, OpenStack and OSM primitives;
* Basic knowledge on bash scripts, Yaml descriptors and Python.

## Tutorials 

Here, we will give you a pipeline to follow so you can fully understand our tutorials.

### Build your VNF from scratch 

This tutorial will allow you to understand how to create a basic VNF from scratch. 

You will learn how to:

* Install OSM and add a VIM account;
* The basic parts of a VNF;
* Create the VNF package, with detailed explanation of the descriptor;
* Create and understand the cloud-init files;
* Create the NS package, with detailed explanation of the descriptor;
* Validating and uploading the packages.

### Introducing OSM primitives and Juju charms

After learning how to build a VNF, this tutorial is very useful to be able to make several configurations in your VNF.

You will learn how to:

* Use OSM primitives to perform VNF operations;
* Build a juju charm, with detailed description of each part of the charm;
* Test the functionality of the charm;
* Execute actions from the charm in your VNF.

### Day-1 and Day-2 VNF operations

After creating and testing the juju charm, we will know add it to our VNF to automatically execute actions.

You will learn how to:

* Understand the day-1 and day-2 operations in VNFs;
* Change the code to add the actions needed;
* Test if the actions were successfully performed.

### How to test your VNFs with the Robot Framework

At this point you learned how to create, test and automate a VNF. Now, is time to test the connections between multiple VNFs.

In this tutorial, you will learn how to:

* Understand the Robot framework and what it can do;
* Use the robot framework to build a jitter test between 2 VNFs;
* Run the test and explore the results.

### How to manage your VNF with an Helm Chart-based Execution Environment (EE)

In this tutorial, you will:

* Understand how Execution Environments works in OSM;
* Create day-1/day-2 primitives via Ansible;
* Perform both day-1/day-2 operations in a VNF.

### From a Helm Chart to a CNF

In this tutorial, you will:

* Understand what is a CNF
* Understand how does a CNF work in the context of OSM
* Learn how to deploy a CNF from a Helm Chart

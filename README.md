# PvS Control Engine with Information Flow Control

This repository contains a functional implementation of the Control Engine for the PvS project. Moreover, this Control Engine is platform independent and can be used along with other data plane abstractions, such as a Mininet topology. A module for Information Flow Control to protect agains CAP attacks is also added on the [inf_flow_ctrl] folder.

## Installation Instructions

It is recommended to install all dependencies with the provided script:

```sh
$ ./scripts/install_dependencies.sh
```

## Starting the P4Runtime Server

To run the server, execute the commands:

```sh
$ sudo su
$ ./run_p4runtime_server.sh
```

## Running SDN Apps

The [examples/sdn_apps] folder contains examples of SDN applications. The [examples/sdn_apps/test_case] folder contains a scenario with a defined Mininet/bmv2 topology for testing of the system.

[//]: # "Links"

[Ubuntu 16.04 or 18.04]: <https://releases.ubuntu.com/>
[gRPC]: <https://grpc.io/docs/quickstart/python/>
[Protobuf]: <https://github.com/protocolbuffers/protobuf>
[PI]: <https://github.com/p4lang/PI>
[Python 2.7]: <https://www.python.org/>

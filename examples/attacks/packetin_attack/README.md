# CAP Attack Scenario in PvS - Reactive Forwarding App

This tutorial proposes to show how to run the scenario where a malicious application called "trigger" performs the CAP attack in known use cases in ONOS: Reactive Forwarding App (fwd).
## System Files
The files for this CAP attack are divided between the malicious application, and the Reactive Forwarding use case. To run the tutorial, firstly we need to place the files in the right folder. The folder containing the Reactive Forwarding code, place the code in:

```sh
$ /home/user/onos/apps
```

For the malicious application "trigger", place the code inside the p4-tutorials folder:
```sh
$ /home/user/onos/apps/p4-tutorial
```

Besides these applications, ONOS needs to have a pipeline configuration that is used in the data plane. Hence, we are using the [pipeline configuration]. Place this code inside the p4-tutorials as well.

At last, bazel builds the ONOS applications by an OAR file. The file "modules.bzl" contains all the applications, and other features that are built. Make sure that the applications have the propper names to avoid errors.

The file is located inside the bazel folder:
```sh
/home/user/onos/tools/build/bazel/
```
In the APP_MAP of the file, add the following if they do not exist:
```sh
"//apps/p4-tutorial/trigger:onos-apps-p4-tutorial-trigger-oar": [],
"//apps/p4-tutorial/pipeconf:onos-apps-p4-tutorial-pipeconf-oar": [],
"//apps/p4-tutorial/int:onos-apps-p4-tutorial-int-oar": [],
```

## Integrating ONOS functionalities and PvS

Starting the tutorial, we firstly execute ONOS.

On the terminal 1, we're going to build and execute ONOS with bazel.
```sh
$ bazel build onos
$ bazel run onos-local -- clean debug
```
If the environment variables are set in your computer, you may also use the "ok" command, which is an alias to run ONOS locally.

On the terminal 2, we're going to enter ONOS CLI to activate drivers and applications.
 ```sh
$ ssh -p 8101 karaf@localhost
```
Since we don't need LLDP app, we will deactivate it. Also, the bmv2 driver needs to be started.
After you're logged in, run the following commands:
```
onos> app deactivate org.onosproject.lldpprovider
onos> app activate org.onosproject.drivers.bmv2
```

You can see all the applications and drivers that are enabled in ONOS, by using the command:
```
onos> apps -s -a
```
Make sure that the bmv2 driver is enabled, and also p4runtime drivers, such as bellow:
```
*   3 org.onosproject.yang                 2.4.0.SNAPSHOT YANG Compiler and Runtime
*   4 org.onosproject.config               2.4.0.SNAPSHOT Dynamic Configuration
*   6 org.onosproject.faultmanagement      2.4.0.SNAPSHOT Fault Management
*   8 org.onosproject.optical-model        2.4.0.SNAPSHOT Optical Network Model
*  10 org.onosproject.netconf              2.4.0.SNAPSHOT NETCONF Provider
*  11 org.onosproject.restsb               2.4.0.SNAPSHOT REST Provider
*  12 org.onosproject.models.tapi          2.4.0.SNAPSHOT ONF Transport API YANG Models
*  13 org.onosproject.models.ietf          2.4.0.SNAPSHOT IETF YANG Models
*  14 org.onosproject.models.openconfig    2.4.0.SNAPSHOT OpenConfig YANG Models
*  15 org.onosproject.models.openconfig-infinera 2.4.0.SNAPSHOT OpenConfig Infinera XT3300 YANG Models
*  16 org.onosproject.models.openconfig-odtn 2.4.0.SNAPSHOT OpenConfig RD v0.3 YANG Models
*  17 org.onosproject.odtn-api             2.4.0.SNAPSHOT ODTN API & Utilities Application
*  18 org.onosproject.drivers.netconf      2.4.0.SNAPSHOT Generic NETCONF Drivers
*  19 org.onosproject.drivers              2.4.0.SNAPSHOT Default Drivers
*  20 org.onosproject.drivers.optical      2.4.0.SNAPSHOT Basic Optical Drivers
*  21 org.onosproject.protocols.grpc       2.4.0.SNAPSHOT gRPC Protocol Subsystem
*  22 org.onosproject.protocols.gnmi       2.4.0.SNAPSHOT gNMI Protocol Subsystem
*  23 org.onosproject.generaldeviceprovider 2.4.0.SNAPSHOT General Device Provider
*  24 org.onosproject.drivers.gnmi         2.4.0.SNAPSHOT gNMI Drivers
*  25 org.onosproject.drivers.odtn-driver  2.4.0.SNAPSHOT ODTN Driver
*  35 org.onosproject.protocols.gnoi       2.4.0.SNAPSHOT gNOI Protocol Subsystem
*  36 org.onosproject.drivers.gnoi         2.4.0.SNAPSHOT gNOI Drivers
*  37 org.onosproject.protocols.p4runtime  2.4.0.SNAPSHOT P4Runtime Protocol Subsystem
*  38 org.onosproject.p4runtime            2.4.0.SNAPSHOT P4Runtime Provider
*  39 org.onosproject.drivers.p4runtime    2.4.0.SNAPSHOT P4Runtime Drivers
*  40 org.onosproject.pipelines.basic      2.4.0.SNAPSHOT Basic Pipelines
*  41 org.onosproject.drivers.stratum      2.4.0.SNAPSHOT Stratum Drivers
*  42 org.onosproject.drivers.bmv2         2.4.0.SNAPSHOT BMv2 Drivers
* 114 org.onosproject.gui2                 2.4.0.SNAPSHOT ONOS GUI2
```

In the data plane for this tutorial, there are a virtual switch that contains a L2 Switch code, where in case it matches with an Ethernet dst address, forwards to a certain port.
```
action set_out_port(port_t port) {
        // Specifies the output port for this packet by setting the
        // corresponding metadata.
        standard_metadata.egress_spec = port;
}
    
table t_l2_fwd {
        key = {
            hdr.ethernet.dst_addr: exact;
        }
        actions = {
            set_out_port;
            send_to_cpu;
            _drop;
            NoAction;
        }
        default_action = NoAction();
    }
```
You can see the entire [L2 Switch p4 code], and the [pipeline configuration] that is used in ONOS.

Continuing the tutorial, we need to activate the L2 example Pipeconf in the ONOS CLI:
```
onos> app activate org.onosproject.p4tutorial.pipeconf
```

With the L2's pipeconf set, we are able to do packet I/O operations. 

On terminal 3, we're going to build the L2 bmv2 exercise by emulating the Mininet:
```sh
$ cd /home/user/p4runtime-grpc-v3/examples/attacks/bmv2/exercises/l2/
$ make all
```
After the mininet is instantiated, the topology information is sent to ONOS, and the table entries are already deployed, so a ping test should work.

To see the impact of the CAP attack, we're following the instruction of creating flow between two hosts which will be impacted by the attack. 
```sh
$ xterm h11 h111 s2
```
In the xterm of h11, start the iperf3 server:
```sh
$ iperf3 -s
```

In the xterm of h111, start the iperf3 client:
```sh
$ iperf3 -c 10.0.1.11 -u -t 0
```

You can see the flow occuring between the two hosts.

In the xterm of s2, start a tcpdump:
```sh
$ tcpdump -i s2-eth3
```

Following the tutorial, in terminal 4, we're iniciating the PvS Control Engine which listens to connections in the 50051 port. 
Instantiate the server:
```sh
$ ./run_p4runtime_server.sh
```

The configuration is done. After, ONOS will be informed of the devices and initial P4Runtime requests can be made, containing Stream Channel Requests and Packet I/O.

### Reactive Forwarding App (fwd)

The fwd application works by intercepting packets that arrive from the data plane, and generating a flow rule according to the packet.  In case a CAP attack occurs, the reactive forwarding app will perform the malicious bogus action.

In the ONOS CLI, we need to activate the reactive forwarding app:
```
onos> app activate org.onosproject.fwd
```
```
You should see some information about the application in the ONOS log about disabled matching features, and flow rule priorities:
2020-09-24T16:22:40,638 | INFO  | CM Event Dispatcher (Fire ConfigurationEvent: pid=org.onosproject.fwd.ReactiveForwarding) | ReactiveForwarding               | 212 - org.onosproject.onos-apps-fwd - 2.4.0.SNAPSHOT | Configured. Packet-out only forwarding is disabled
2020-09-24T16:22:40,639 | INFO  | CM Event Dispatcher (Fire ConfigurationEvent: pid=org.onosproject.fwd.ReactiveForwarding) | ReactiveForwarding               | 212 - org.onosproject.onos-apps-fwd - 2.4.0.SNAPSHOT | Configured. Forwarding using OFPP_TABLE port is disabled
2020-09-24T16:22:40,639 | INFO  | CM Event Dispatcher (Fire ConfigurationEvent: pid=org.onosproject.fwd.ReactiveForwarding) | ReactiveForwarding               | 212 - org.onosproject.onos-apps-fwd - 2.4.0.SNAPSHOT | Configured. IPv6 forwarding is disabled
2020-09-24T16:22:40,639 | INFO  | CM Event Dispatcher (Fire ConfigurationEvent: pid=org.onosproject.fwd.ReactiveForwarding) | ReactiveForwarding               | 212 - org.onosproject.onos-apps-fwd - 2.4.0.SNAPSHOT | Configured. Match Dst MAC Only is enabled
2020-09-24T16:22:40,640 | INFO  | CM Event Dispatcher (Fire ConfigurationEvent: pid=org.onosproject.fwd.ReactiveForwarding) | ReactiveForwarding               | 212 - org.onosproject.onos-apps-fwd - 2.4.0.SNAPSHOT | Configured. Matching Vlan ID is disabled
2020-09-24T16:22:40,640 | INFO  | CM Event Dispatcher (Fire ConfigurationEvent: pid=org.onosproject.fwd.ReactiveForwarding) | ReactiveForwarding               | 212 - org.onosproject.onos-apps-fwd - 2.4.0.SNAPSHOT | Configured. Matching IPv4 Addresses is disabled
2020-09-24T16:22:40,640 | INFO  | CM Event Dispatcher (Fire ConfigurationEvent: pid=org.onosproject.fwd.ReactiveForwarding) | ReactiveForwarding               | 212 - org.onosproject.onos-apps-fwd - 2.4.0.SNAPSHOT | Configured. Matching IPv4 DSCP and ECN is disabled
2020-09-24T16:22:40,640 | INFO  | CM Event Dispatcher (Fire ConfigurationEvent: pid=org.onosproject.fwd.ReactiveForwarding) | ReactiveForwarding               | 212 - org.onosproject.onos-apps-fwd - 2.4.0.SNAPSHOT | Configured. Matching IPv6 Addresses is disabled
2020-09-24T16:22:40,641 | INFO  | CM Event Dispatcher (Fire ConfigurationEvent: pid=org.onosproject.fwd.ReactiveForwarding) | ReactiveForwarding               | 212 - org.onosproject.onos-apps-fwd - 2.4.0.SNAPSHOT | Configured. Matching IPv6 FlowLabel is disabled
2020-09-24T16:22:40,641 | INFO  | CM Event Dispatcher (Fire ConfigurationEvent: pid=org.onosproject.fwd.ReactiveForwarding) | ReactiveForwarding               | 212 - org.onosproject.onos-apps-fwd - 2.4.0.SNAPSHOT | Configured. Matching TCP/UDP fields is disabled
2020-09-24T16:22:40,641 | INFO  | CM Event Dispatcher (Fire ConfigurationEvent: pid=org.onosproject.fwd.ReactiveForwarding) | ReactiveForwarding               | 212 - org.onosproject.onos-apps-fwd - 2.4.0.SNAPSHOT | Configured. Matching ICMP (v4 and v6) fields is disabled
2020-09-24T16:22:40,641 | INFO  | CM Event Dispatcher (Fire ConfigurationEvent: pid=org.onosproject.fwd.ReactiveForwarding) | ReactiveForwarding               | 212 - org.onosproject.onos-apps-fwd - 2.4.0.SNAPSHOT | Configured. Ignore IPv4 multicast packets is disabled
2020-09-24T16:22:40,641 | INFO  | CM Event Dispatcher (Fire ConfigurationEvent: pid=org.onosproject.fwd.ReactiveForwarding) | ReactiveForwarding               | 212 - org.onosproject.onos-apps-fwd - 2.4.0.SNAPSHOT | Configured. record metrics  is disabled
2020-09-24T16:22:40,642 | INFO  | CM Event Dispatcher (Fire ConfigurationEvent: pid=org.onosproject.fwd.ReactiveForwarding) | ReactiveForwarding               | 212 - org.onosproject.onos-apps-fwd - 2.4.0.SNAPSHOT | Configured. Flow Timeout is configured to 10 seconds
2020-09-24T16:22:40,643 | INFO  | CM Event Dispatcher (Fire ConfigurationEvent: pid=org.onosproject.fwd.ReactiveForwarding) | ReactiveForwarding               | 212 - org.onosproject.onos-apps-fwd - 2.4.0.SNAPSHOT | Configured. Flow Priority is configured to 10
2020-09-24T16:22:40,643 | WARN  | CM Event Dispatcher (Fire ConfigurationEvent: pid=org.onosproject.fwd.ReactiveForwarding) | ReactiveForwarding               | 212 - org.onosproject.onos-apps-fwd - 2.4.0.SNAPSHOT | org.onosproject.net.flow.DefaultTrafficSelector$Builder@28f11693
```


## Activate the Malicious App

In the ONOS CLI, we will activate the malicious app to perform a malicious ARP reply that will disrupt the behavior of the virtual switch.
```
onos> app activate org.onosproject.p4tutorial.trigger
```
This malicious application performs a packet-out operation that was manually crafted with an ARP reply. 

In response, the virtual switch will perform a packet-in operation to the legitimate application. 

You should see in the ONOS log the packet-in arriving, and then the malicious flow rule being created by the fwd app, and the respective P4Runtime Write Request in the PvS.
```
device_id: 1
election_id {
  low: 1
}
updates {
  type: INSERT
  entity {
    table_entry {
      table_id: 44918510
      match {
        field_id: 1
        exact {
          value: "\010\000\000\000\001\021"
        }
      }
      action {
        action {
          action_id: 20071142
          params {
            param_id: 1
            value: "\000\003"
          }
        }
      }
    }
  }
}
```
The malicious operation made the reactive forwarding application to perform a bogus flow rule that disrupts the data plane behaviour. The operation changed the egress port when a match with an ethernet dst address was made.
You can see the flow disrupted between the two hosts, and the s2's xterm terminal showing the flow that was diverted.

[//]: # "Links"
[L2 Switch p4 code]: <https://github.com/guilherme6041/p4runtime-grpc-v3/blob/master/examples/pvs-onos/onos-app/pipeconf/src/main/resources/l2_switch.p4>
[pipeline configuration]: <https://github.com/guilherme6041/p4runtime-grpc-v3/tree/master/examples/pvs-onos/onos-app/pipeconf>


# CAP Attack Scenario in PvS - Inband Telemetry App

This tutorial proposes to show how to run the scenario where a malicious application called "trigger" performs the CAP attack in known use cases in ONOS: Inband Telemetry App (INT).

## System Files
The files for this CAP attack are divided between the malicious application, and the Inband Telemetry (INT) use case. To run the tutorial, firstly we need to place the files in the right folder. The folders containing the Inband telemetry code and the malicious application "trigger" were created inside the p4-tutorials folder, so place the code of both folders in:
```sh
$ /home/user/onos/apps/p4-tutorial/
```

Since, we are using the bmv2 in the data plane, you may place the bmv2 code in any folder. One small change that you may need to perform is to change the path of the [MRI json] netcfg file in the [run_exercise] file. Mininet sends this file to ONOS, so it can discover the switches information. 

Place the [MRI json] file in a folder, and set the right path for the variable "TEMP_NETCFG_FILE" in the [run_exercise] file. The file is located inside the utils folder of the bmv2:
```sh
vim /home/user/Documents/tutorials/utils/run_exercise.py
```
The "TEMP_NETCFG_FILE" may look like for example:
```
TEMP_NETCFG_FILE = '/home/guilherme/Documents/p4tutorial_mininet.json'
```

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
Starting the tutorial, we run ONOS.

On the terminal 1, we're going to build and execute ONOS.
```sh
$ bazel build onos
$ bazel run onos-local -- clean debug
```
If the environment variables are set in your computer, you may also use the "ok" command, which is an alias to run ONOS locally.

On the terminal 2, we're going to enter ONOS CLI to activate drivers and applications.
```sh
$ ssh -p 8101 karaf@localhost
```
Since we don't need LLDP app, we will deactivate it. Also, the bmv2 driver needs to be started. After you're logged in, run the following commands:

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

We are using the bmv2 in the data plane containing three virtual switches that are emulated in Mininet. These switches are populated with a p4 code that performs Multi-Hop Route Inspection (MRI), that captures switch id information, and the queue depth of each switch. The code works by inserting a switch trace of the packet's route in egress processing of the switch.
```sh
action add_swtrace(switchID_t swid) { 
        hdr.mri.count = hdr.mri.count + 1;
        hdr.swtraces.push_front(1);
        // According to the P4_16 spec, pushed elements are invalid, so we need
        // to call setValid(). Older bmv2 versions would mark the new header(s)
        // valid automatically (P4_14 behavior), but starting with version 1.11,
        // bmv2 conforms with the P4_16 spec.
        hdr.swtraces[0].setValid();
        hdr.swtraces[0].swid = swid;
        hdr.swtraces[0].qdepth = (qdepth_t)standard_metadata.deq_qdepth;

        hdr.ipv4.ihl = hdr.ipv4.ihl + 2;
        hdr.ipv4_option.optionLength = hdr.ipv4_option.optionLength + 8; 
    	hdr.ipv4.totalLen = hdr.ipv4.totalLen + 8;
    }

    table swtrace {
        actions = { 
        	add_swtrace; 
        	NoAction; 
        }
        default_action = NoAction();      
    }
```

You may see the entire [MRI p4] code, and the [MRI directory] with instructions.

Continuing the tutorial, we need to activate the Pipeconf, along with the INT application that monitors the switches:
```
onos> app activate org.onosproject.p4tutorial.pipeconf
onos> app activate org.onosproject.p4tutorial.int
```

On terminal 3, we're going to build the MRI bmv2 exercise by emulating the Mininet:
```sh
$ cd /home/user/Documents/tutorials/exercises/mri/
$ make all
```
After the mininet is instantiated, the topology information is sent to ONOS, and the table entries are already deployed, so a ping test should work.

Following the MRI P4 tutorial, we're following the instruction of creating flow between S1-S2 too see the normal queue size that is captured by the MRI application. In which, later we'll see the impact of the CAP attack.
```sh
$ xterm h11 h22
```

In the xterm of h22, start the iperf3 server:
```sh
$ iperf3 -s
```

In the xterm of h11, start the iperf3 client:
```sh
$ iperf3 -c 10.0.2.22 -u -t 0 -b 256K -l 8K
```

You can see the flow occuring between S1-S2.

Continuing the tutorial, on terminal 4, we're iniciating the PvS Control Engine which listens to connections in the 50051 port. Firstly, make sure the PACKETIN_IFACE and the PACKETOUT_IFACE are set correct:
```sh
$ vim p4runtime-grpc-v3/config/ServerConfig.py
$ PACKETIN_IFACE = "s2-eth2"
$ PACKETOUT_IFACE = "s1-eth2"
```

Then, instantiate the server:
```sh
$ ./run_p4runtime_server.sh
```


## Activate the Malicious App

In the ONOS CLI, we will activate the malicious app to perform a least privileged action in the virtual switch that it has access to.

```
onos> app activate org.onosproject.p4tutorial.trigger

```

This malicious application performs a packet-out operation that was manually crafted to do a "out-of-band", and containing fake MRI data, that will reach the other virtual switch.

In response, the virtual switch will perform a packet-in operation to the legitimate application INT, and a bogus action will be performed.

## Inband Telemetry App (INT)

The INT application works by monitoring the switch id and queue depth information of the switches. Considering a high queue depth of a switch, the application performs actions to normalize it. 

Due to the "out-of-band" flow, the INT application receives the packet-in with the fake MRI data, more specifically a high queue rate that wouldn't be normal, and supposes that it's from the legitimate virtual.

The INT ONOS application receives the packet, and analyses the queue depth:
```
####### [ INT ] ######
	### [ SwitchTrace ] ###
	    swid = 1
            qdepth = 4000
    ### [ SwitchTrace ] ###
            swid = 2
            qdepth = 0
```

In response for the high queue depth, the application performs an action to normalize it by redirecting the flow of the legitimate virtual switch.
You may see that the INT application created a flow rule redirecting the flow to another port.
```
device_id: 1
election_id {
  low: 1
}
updates {
  type: INSERT
  entity {
    table_entry {
      table_id: 37375156
      match {
        field_id: 1
        lpm {
          value: "\n\000\002\026"
          prefix_len: 32
        }
      }
      action {
        action {
          action_id: 28792405
          params {
            param_id: 2
            value: "\000\004"
          }
          params {
            param_id: 1
            value: "\010\000\000\000\002\""
          }
        }
      }
    }
  }
}

```

At last, open another terminal, and run the file to install the malicious flow rule into the bmv2 switch.
```sh
$ cd /home/user/Documents/tutorials/exercises/mri
$ ./mycontroller.py --p4info build/mri.p4.p4info.txt --bmv2-json build/mri.json
```
After this malicious operation is performed, you may see that the h11's iperf with h22 will not be working.



[//]: # "Links"

[run_exercise]: <https://github.com/guilherme6041/p4runtime-grpc-v3/blob/master/examples/attacks/int_attack/bmv2/utils/run_exercise.py>
[MRI json]: <https://github.com/guilherme6041/p4runtime-grpc-v3/blob/master/examples/attacks/int_attack/bmv2/p4tutorial_mininet.json>
[MRI p4]: <https://github.com/guilherme6041/p4runtime-grpc-v3/blob/master/examples/attacks/int_attack/bmv2/exercises/mri/mri.p4>
[MRI directory]: <https://github.com/guilherme6041/p4runtime-grpc-v3/tree/master/examples/attacks/int_attack/bmv2/exercises/mri>

# Print commands and exit on errors
set -xe

cd $HOME

# Clear repos
sudo rm -rf p4c/
sudo rm -rf grpc/
sudo rm -rf behavioral-model/
sudo rm -rf protobuf/
sudo rm -rf PI/
sudo rm -rf p4runtime-grpc-v3/

gsettings set org.gnome.desktop.session idle-delay 0
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-timeout 0
gsettings set com.canonical.Unity.Launcher favorites "['application://org.gnome.Nautilus.desktop', 'application://firefox.desktop', 'unity://running-apps', 'application://gnome-terminal.desktop', 'application://gnome-system-monitor.desktop', 'unity://expo-icon', 'unity://devices']"

wget https://bootstrap.pypa.io/pip/2.7/get-pip.py
python ./get-pip.py
rm get-pip.py

sudo apt-get clean
sudo apt-get update

sudo apt-get install -y git

# --- PvS --- #
git clone -b pvs_bmv2 https://github.com/guilherme6041/p4runtime-grpc-v3/
cd p4runtime-grpc-v3
git checkout 73167a87ff68ce6cdb3f8dae8a778c6875af430c
cd ..

KERNEL=$(uname -r)
sudo apt-get install -y --no-install-recommends --fix-missing autoconf automake bison build-essential ca-certificates cmake cpp curl flex iperf3 libboost-dev libboost-filesystem-dev libboost-iostreams-dev libboost-program-options-dev libboost-system-dev libboost-test-dev libboost-thread-dev libc6-dev libevent-dev libffi-dev libfl-dev libgc-dev libgc1c2 libgflags-dev libgmp-dev libgmp10 libgmpxx4ldbl libjudy-dev libpcap-dev libreadline6 libreadline6-dev libssl-dev libtool linux-headers-$KERNEL make mktemp pkg-config python python-dev python-ipaddr python-libpcap python-pip python-psutil python-scapy python-setuptools tcpdump unzip vim wget zlib1g-dev

#Src
BMV2_COMMIT="0a69227f1b0fee845f859dcf59f01291d64784d5"
PI_COMMIT="4546038f5770e84dc0d2bba90f1ee7811c9955df"
P4C_COMMIT="64b04c8687c22a0eccf8ff3ad056f7d4a19dfa5d"
PROTOBUF_COMMIT="48cb18e5c419ddd23d9badcfe4e9df7bde1979b2"
GRPC_COMMIT="c7cc34e2d76afe67528ac5b20c5ccbe0692757e8"

#Get the number of cores to speed up the compilation process
NUM_CORES=`grep -c ^processor /proc/cpuinfo`

# --- Mininet --- #
git clone git://github.com/mininet/mininet mininet
sudo ./mininet/util/install.sh -nwv

# --- Protobuf --- #
git clone https://github.com/google/protobuf.git
cd protobuf
git checkout ${PROTOBUF_COMMIT}
export CFLAGS="-Os"
export CXXFLAGS="-Os"
export LDFLAGS="-Wl,-s"
./autogen.sh
./configure --prefix=/usr
make -j${NUM_CORES}
sudo make install
sudo ldconfig
unset CFLAGS CXXFLAGS LDFLAGS
# Force install python module
cd python
sudo python setup.py install
cd ../..

# Necessary pip packages
sudo pip install protobuf==3.11.3

# --- gRPC --- #
git clone https://github.com/grpc/grpc.git
cd grpc
git checkout ${GRPC_COMMIT}
git submodule update --init --recursive
export LDFLAGS="-Wl,-s"
make -j${NUM_CORES}
sudo make install
sudo ldconfig
unset LDFLAGS
cd ..
# Install gRPC Python Package
sudo pip install grpcio==1.28.1

# --- BMv2 deps (needed by PI) --- #
git clone https://github.com/p4lang/behavioral-model.git
cd behavioral-model
git checkout ${BMV2_COMMIT}
# From bmv2's install_deps.sh, we can skip apt-get install.
# Nanomsg is required by p4runtime, p4runtime is needed by BMv2...
tmpdir=`mktemp -d -p .`
cd ${tmpdir}
bash ../travis/install-thrift.sh
bash ../travis/install-nanomsg.sh
sudo ldconfig
bash ../travis/install-nnpy.sh
cd ..
sudo rm -rf $tmpdir
cd ..

# --- PI/P4Runtime --- #
git clone https://github.com/p4lang/PI.git
cd PI
git checkout ${PI_COMMIT}
git submodule update --init --recursive
./autogen.sh
./configure --with-proto
make -j${NUM_CORES}
sudo make install
sudo ldconfig
cd ..

# --- Bmv2 --- #
cd behavioral-model
./autogen.sh
./configure --enable-debugger --with-pi
make -j${NUM_CORES}
sudo make install
sudo ldconfig
# Simple_switch_grpc target
cd targets/simple_switch_grpc
./autogen.sh
./configure --with-thrift
make -j${NUM_CORES}
sudo make install
sudo ldconfig
cd ../../..

# --- P4C --- #
git clone https://github.com/p4lang/p4c
cd p4c
git checkout ${P4C_COMMIT}
git submodule update --init --recursive
mkdir -p build
cd build
cmake ..
make -j2
sudo make install
sudo ldconfig
cd ../..

# Clear repos
sudo rm -rf p4c/
sudo rm -rf grpc/
sudo rm -rf behavioral-model/
sudo rm -rf protobuf/
sudo rm -rf PI/

sudo pip install grpcio-tools==1.28.1

# --- Bazel --- #
wget https://github.com/bazelbuild/bazelisk/releases/download/v1.4.0/bazelisk-linux-amd64
chmod +x bazelisk-linux-amd64
sudo mv bazelisk-linux-amd64 /usr/local/bin/bazel

# --- Onos 2.4.0 --- #
git clone https://gerrit.onosproject.org/onos
cd onos
git checkout f8e74184e0876d9d0309b7fe0bd8452d1ec5947d
cd ..

rm -rf onos/protocols/p4runtime/ctl/src/main/java/org/onosproject/p4runtime/ctl/client
cp -r p4runtime-grpc-v3/examples/pvs-onos/onos-drvs/protocols/p4runtime onos/protocols/p4runtime/ctl/src/main/java/org/onosproject/p4runtime/ctl/client
cp p4runtime-grpc-v3/examples/pvs-onos/onos-drvs/protobufs/AuthOuterClass.java onos/protocols/p4runtime/ctl/src/main/java/org/onosproject/p4runtime/ctl/controller/.

# --- Reactive Forwarding Attack --- #
rm -rf onos/apps/fwd
rm -rf onos/apps/p4-tutorial/pipeconf
cp -r p4runtime-grpc-v3/examples/attacks/packetin_attack/use_case/fwd onos/apps/fwd
cp -r p4runtime-grpc-v3/examples/attacks/packetin_attack/use_case/pipeconf onos/apps/p4-tutorial/pipeconf
cp -r p4runtime-grpc-v3/examples/attacks/packetin_attack/malicious_app/trigger onos/apps/p4-tutorial/trigger

cp -r p4runtime-grpc-v3/examples/attacks/int_attack/use_case/int onos/apps/p4-tutorial/int

sed -i 's+"//apps/p4-tutorial/pipeconf:onos-apps-p4-tutorial-pipeconf-oar": \[],+"//apps/p4-tutorial/trigger:onos-apps-p4-tutorial-trigger-oar": \[],\n    "//apps/p4-tutorial/pipeconf:onos-apps-p4-tutorial-pipeconf-oar": [],\n    "//apps/p4-tutorial/int:onos-apps-p4-tutorial-int-oar": [],+g' onos/tools/build/bazel/modules.bzl

cd onos
bazel build onos
cd ..

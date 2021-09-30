N_SWITCHES=$1

set -xe

rm -f log.txt
rm -f Mininet/*.json
./createExp --switches $N_SWITCHES
cp LoadVSwitch.py ../../../examples/virtual_switches/LoadVSwitch.py

sudo gnome-terminal -e ./scripts/mininet.sh
sleep $((10 + $N_SWITCHES))
sudo gnome-terminal -e ./scripts/pvs.sh
sleep 5
sudo gnome-terminal -e ./scripts/client_admin.sh
sleep 3
sudo gnome-terminal -e ./scripts/client_trigger.sh
sleep 30

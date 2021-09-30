set -xe

counts=('5' '10' '15' '20' '25' '30' '35' '40' '45' '50')

rm -rf Logs

mkdir -p Logs
mkdir -p Logs/vIFC-True
mkdir -p Logs/vIFC-False

g++ -O2 -std=c++11 -o createExp createExp.cpp
g++ -O2 -std=c++11 -o logTimes logTimes.cpp

echo "vIFC True"
cp scripts/ServerConfigTrue.py ../../../config/ServerConfig.py
for (( k=0; k<${#counts[@]}; k++ ))
do
  N=${counts[$k]}

  echo "Run "$(($k + 1))

  ./run_exp.sh $N
  mv log.txt Logs/vIFC-True/log$N.txt
  sleep 5
done

echo "vIFC False"
cp scripts/ServerConfigFalse.py ../../../config/ServerConfig.py
for (( k=0; k<${#counts[@]}; k++ ))
do
  N=${counts[$k]}

  echo "Run "$(($k + 1))

  ./run_exp.sh $N
  mv log.txt Logs/vIFC-False/log$N.txt
  sleep 5
done

cd Mininet
sudo make clean
rm *.json
cd ..

./logTimes
cd Plot
gnuplot plot.plot
epstopdf plot.eps
rm plot.eps
cd ..

rm createExp logTimes
rm LoadVSwitch.py
cp scripts/ServerConfigTrue.py ../../../config/ServerConfig.py

echo "Plot at Plot/plot.pdf"

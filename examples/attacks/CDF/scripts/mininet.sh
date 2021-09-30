cd Mininet
make clean
make << EOF
  sh sleep 40
  exit
EOF

cd ../../../
sudo su << EOF
  rm -f logs/*
  rm database.db
  timeout --signal=SIGINT 30 ./run_p4runtime_server.sh
  sleep 3
  exit
EOF

mv logs/* examples/attacks/CDF/log.txt

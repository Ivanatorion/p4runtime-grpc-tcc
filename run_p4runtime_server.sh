#!/bin/bash

set -xe
source scripts/export_vars.sh
python server/grpc_server.py

#!/bin/bash

cwd=$(pwd)

# open new terminal to run model script
osascript -e "tell application \"Terminal\" to do script \"cd '$cwd' && python3 api/run_model.py\""

sleep 10

# open new terminal to run integration test
osascript -e "tell application \"Terminal\" to do script \"cd '$cwd' && pytest api/integration_test.py\""
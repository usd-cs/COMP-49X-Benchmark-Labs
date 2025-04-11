#!/bin/bash

# ONLY WORKS ON MAC
# to run do "bash mac_end_test.bash" without quotes

# Get the current working directory
cwd=$(pwd)

# open new terminal to run model script
osascript -e "tell application \"Terminal\" to do script \"cd '$cwd' && python3 api/run_model.py\""

# wait for model to load
sleep 10

# open new terminal to run website script
osascript -e "tell application \"Terminal\" to do script \"cd '$cwd' && python3 website/website.py\""

# wait for website to load
sleep 10

# open new terminal and run pytest
osascript -e "tell application \"Terminal\" to do script \"cd '$cwd' && pytest api/end_test.py\""
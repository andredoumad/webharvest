#!/bin/bash
source /home/ubuntu/webharvest/bin/activate && cd /home/ubuntu/webharvest/ && python webharvest_robot_router_websocket.py >> /home/ubuntu/webharvest/webharvest_shell.log 2>&1
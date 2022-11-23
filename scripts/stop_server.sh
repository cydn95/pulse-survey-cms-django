#!/bin/bash
# this file runs first, so during an initail installation error might happen
cd /home/ubuntu/github-app/Pulse-CMS


echo "##################################################################"
echo "Stopping Python Server"
echo "##################################################################"

sudo pkill gunicorn

echo "##################################################################"
echo "Python Server Stopped"
echo "##################################################################"



#!/bin/bash
cd /home/ubuntu/github-app/Pulse-CMS
echo "##########################################################################"
echo "Starting Server"
echo "##########################################################################"

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile

echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile

echo 'eval "$(pyenv init -)"' >> ~/.bash_profile

echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bash_profile

. ~/.bash_profile
. ~/.profile

pyenv activate pulse-backend-dev-3.7.14

gunicorn --bind 0.0.0.0:8000 --workers=3 --threads=2 mysite.wsgi:application --daemon

pyenv deactivate
echo "##########################################################################"
echo "Python Server Started at 8000 port"
echo "##########################################################################"

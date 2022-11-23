#!/bin/bash

cd /home/ubuntu/github-app/Pulse-CMS

echo "##########################################################################"
echo Installing Dependencies
echo "##########################################################################"

sudo apt update -y

sudo apt install make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev -y


git clone https://github.com/pyenv/pyenv.git ~/.pyenv

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile

echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile

echo 'eval "$(pyenv init -)"' >> ~/.bash_profile

. ~/.bash_profile
. ~/.bashrc
. ~/.profile

python_version=$(eval pyenv local)

if [[ "$python_version" == "3.7.14" ]] ;then
    echo "PYTHON VERSION $python_version Exists"
else
    pyenv install 3.7.14 --verbose
    pyenv local 3.7.14
fi

git clone https://github.com/pyenv/pyenv-virtualenv.git $(pyenv root)/plugins/pyenv-virtualenv

echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bash_profile

. ~/.bash_profile
. ~/.bashrc
. ~/.profile

pyenv virtualenv 3.7.14 pulse-backend-dev-3.7.14

pyenv activate pulse-backend-dev-3.7.14

pip install -r requirements.txt

pyenv deactivate
echo "##########################################################################"
echo Done with Installing Dependencies
echo "##########################################################################"

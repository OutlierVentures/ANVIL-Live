#!/bin/bash

onred='\033[41m'
ongreen='\033[42m'
onyellow='\033[43m'
endcolor="\033[0m"

# Handle errors
set -e
error_report() {
    echo -e "${onred}Error: failed on line $1.$endcolor"
}
trap 'error_report $LINENO' ERR

if [ "`whoami`" != "root" ]; then 
	echo "Please run this script with superuser privileges (e.g. 'sudo ./setup.sh')."
	exit 1 
fi

cd /root
git clone https://github.com/OutlierVentures/ANVIL.git
cp demo.ipynb ./ANVIL/anvil/demo.ipynb
cp -a ./charging_service/. ./ANVIL/anvil/charging_service
cp -a ./img/. ./ANVIL/anvil/img
cd ANVIL
./scripts/install.sh
pip3 install jupyter jupyterthemes
jt -t oceans16

jupyter notebook --generate-config

echo "c.NotebookApp.allow_root = True
c.NotebookApp.certfile = u'$PEM_FILE_PATH'
c.NotebookApp.ip = '0.0.0.0'
c.NotebookApp.keyfile = u'$KEY_FILE_PATH'
c.NotebookApp.open_browser = False
c.NotebookApp.port = 443" >> /root/.jupyter/jupyter_notebook_config.py

echo -e "${ongreen}ANVIL-Live installed.${endcolor}"

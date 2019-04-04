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

git clone https://github.com/OutlierVentures/ANVIL.git
cp demo.ipynb ./ANVIL/anvil/demo.ipynb
cp -a ./charging_service/. ./ANVIL/anvil/charging_service
cp -a ./img/. ./ANVIL/anvil/img
cd ANVIL
./scripts/install.sh
pip3 install jupyter jupyterthemes
jt -t oceans16

echo -e "${ongreen}ANVIL-Live installed.${endcolor}"

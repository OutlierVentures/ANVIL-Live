# ANVIL-Live

Live demo of the ANVIL API for electric cars.

## Requirements

- Linux/MacOS and Docker.

## Install and run

Clone ANVIL and add the demo agent:
```
git clone https://github.com/OutlierVentures/ANVIL.git
cp demo.py ./ANVIL/anvil/demo.py
cp demo.html ./ANVIL/anvil/templates/demo.html
cp demo.css ./ANVIL/anvil/static/demo.css
```

Start a Docker container with the cointents of the ANVIL folder mapping port 5004 (demo) to 443 (HTTPS). In the setup, run `./scripts/install.sh` and for the final run command use `cd anvil && python3 demo.py`.

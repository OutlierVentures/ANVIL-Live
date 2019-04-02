# ANVIL-Live

Live demo of the ANVIL API for electric cars.

## Requirements

- Linux/MacOS and Docker.

## Install

1. Set up a firewall, allowing port `443`.
2. Generate a certificate using e.g. LetsEncrypt's `certbot`. Set environment variables specifying the certificate's location:
    ```
    export PEM_FILE_PATH=
    export KEY_FILE_PATH=
    ```
3. `./install.sh`
4. In `ANVIL/anvil/setup.py` add the following before the line defining `_pool`:
    ```
    pool_list = await pool.list_pools()
    for pool_dict in pool_list:
        if pool_dict['pool'] == name:
            return name, 1
    ```
4. Set a notebook password: `jupyter notebook password`


## Run

Start a Fetch.AI node and Sovrin node pool as specified in the ANVIL repo. Note if you have installed ANVIL previously you should start these from the original ANVIL folder.

```
cd ANVIL/anvil
screen
jupyter notebook
```
`CTRL + A`, `CTRL + D` to detach from the screen.

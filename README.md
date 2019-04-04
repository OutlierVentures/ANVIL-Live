# ANVIL-Live

Live code demo of the ANVIL API for electric cars.

## Requirements

- Linux/MacOS and Docker.

## Install

1. `./install.sh`
2. In `ANVIL/anvil/setup.py` add the following before the line defining `_pool`:
    ```
    pool_list = await pool.list_pools()
    for pool_dict in pool_list:
        if pool_dict['pool'] == name:
            return name, 1
    ```


## Run

Start a Fetch.AI node and Sovrin node pool as specified in the ANVIL repo. Note if you have installed ANVIL previously you should start these from the original ANVIL folder.

```
cd ANVIL/anvil
jupyter notebook
```

## Host

You can host the notebook by setting `c.NotebookApp.ip = '0.0.0.0'` in `.jupyter/jupyter_notebook_config.py`. Note that this grants anyone access to arbitrary code execution, so a precompiled mock alternative (below) is recommended. See [here](https://jupyter-notebook.readthedocs.io/en/stable/public_server.html) for using a full live executable.

The alternative is a HTML-ified notebook where you have the outputs prepared beforehand, and display them as the user 'runs' the notebook. See `demo.html` for this safe version.

// TODO: button to show output on execution for each code cell.

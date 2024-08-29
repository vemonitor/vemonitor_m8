# VeMonitor_m8

![CI](https://github.com/vemonitor/vemonitor_m8/actions/workflows/python-package.yml/badge.svg?branch=main)
[![PyPI package](https://img.shields.io/pypi/v/vemonitor_m8.svg)](https://pypi.org/project/vemonitor_m8/)
[![codecov](https://codecov.io/gh/vemonitor/vemonitor_m8/graph/badge.svg?token=M7VgGzkApi)](https://codecov.io/gh/vemonitor/vemonitor_m8)
[![Downloads](https://static.pepy.tech/badge/vemonitor_m8)](https://pepy.tech/project/vemonitor_m8)

> **Note**
> This repository is under active development and is not yet fully tested.

> **Warning**  
> Use this package at your own risk. Misconfiguration or bugs in this application can lead to an excessive number of disk read/writes and/or requests to designated servers (e.g., the EmonCms Server). It is essential that you fully understand and manage:
> - Your VeMonitor configuration file settings.
> - Your Redis server settings.
>
> It is strongly recommended to test your configuration using a monitoring tool like Telegraf/Grafana and Redis/Grafana to supervise and control disk read/writes and HTTP requests, ensuring they follow expected patterns.

VeMonitor M8 is a Python library designed to assist with monitoring solar plant data.

It currently supports:
- Reading and formatting data from:
    - Any device using the Serial Victron Energy VE.Direct text protocol
- Sending the compiled and formatted data to:
    - EmonCms Web Server

A cache system, which can be configured to use either memory or a Redis server, is available to reduce input reads and/or output requests.  

## Installation

To install directly from GitHub:
```
python3 -m pip install "git+https://github.com/vemonitor/vemonitor_m8"
```

To install from PypI :
```
python3 -m pip install vemonitor_m8
```

## Configuration Files

To run this application, you need to provide YAML configuration files. Refer to the [sample configuration files directory](https://github.com/vemonitor/vemonitor_m8/tree/main/config_sample) to understand the overall structure.

All configuration files must be placed in one of the following directories:

On Linux/Unix:
- `/opt/vemonitor_m8/conf/`
- `/opt/vemonitor/conf/`
- `${HOME}/.vemonitor`

On Windows:
- `${HOME}/.vemonitor`

### Structure

You can choose your preferred configuration architecture. You may opt for a single configuration file or divide it into multiple files.

To effectively manage data input/output and server connections, you need to configure at least both `appBlocks` and `appConnectors` in your setup.

Here’s a basic example of the required configuration:

```yaml
    # Configuration for appBlocks
    appBlocks:
        - "(...)"
    
    # Configuration for appConnectors
    # Here, configure both input and output connection data for the necessary workers
    appConnectors:
        "(...)"

```
#### Unique configuration file

If you choose to consolidate all configuration settings into a single file, you can omit the `Import` setting key parameters from the sample configuration example.

To do this, copy the contents of [`vm_appConnectors.yaml`](https://github.com/vemonitor/vemonitor_m8/tree/main/config_sample/vm_appConnectors.yaml) and append it to the end of [`vm_conf.yaml`](https://github.com/vemonitor/vemonitor_m8/tree/main/config_sample/vm_conf.yaml).

Optionally, you can also include the content of other configuration files as needed.

#### Multiple Configuration files
Refer to [sample configuration files directory](https://github.com/vemonitor/vemonitor_m8/tree/main/config_sample) to example of possible structure.

You need to set `Imports` setting parameters on the main configuration file to load needed configuration settings as fallow:

```yaml
    # Imports settings parameters
    # List of file names to load and add to configuration

    Imports:
        # example of batteryBanks settings file
        - "vm_batteryBank.yaml"
        # example of an appConnectors settings file
        - "vm_appConnectors.yaml"
```
> **Note**  
> - All file names must correspond to existing files in the current configuration directory.
> - File names should contain only alphanumeric characters, underscores (`_`), or hyphens (`-`), and must start with an alphanumeric character.
> - Only `.yaml` and `.yml` extensions are accepted.

### Settings

As mentioned above, only two configuration setting keys are required:

- **appBlocks**: Contains the configuration settings for inputs and outputs.
- **appConnectors**: Contains the connection data for inputs and outputs needed by the workers.

Additionally, some optional configuration setting keys are available:

- **Imports**: Used to import external files into the configuration.
- **batteryBanks**: Used by the internal batteryBanks middleware.


## VE.Direct to EmonCms

This example demonstrates how to read data from devices using the Serial VE.Direct text protocol and send the specified data at regular intervals to the [EmonCms](https://emoncms.org/) web application.

> **Note:** You need to install the [Emoncms worker extra package](https://github.com/vemonitor/emon_worker_m8).
```
pip install emon_worker_m8
```
If you want to install and run EmonCms locally, see the [EmonCms repository](https://github.com/emoncms/emoncms).

### Configuration Files

> See the [sample configuration files](https://github.com/vemonitor/vemonitor_m8/tree/main/config_sample/vedirect_to_emoncms).

You can copy these sample configuration files to your own configuration directory and then update them with the necessary settings.

### Running VeMonitor

First, ensure that you have installed any additional worker packages you require.

Next, set up your configuration files in the appropriate configuration directory.

#### How It Works

In the [main sample configuration file](https://github.com/vemonitor/vemonitor_m8/blob/main/config_sample/vedirect_to_emoncms/vm_conf.yaml) (`vm_conf.yaml`), there are two different `AppBlocks`:
- `BatteryMonitor`
- `BatteryAndPannelsMonitor`

For example, you can run `BatteryMonitor` for testing purposes.

Based on the configuration settings, this app will read data from the VE.Direct Serial Device (e.g., BMV700), and the data will be cached on the local Redis server:

- Every second, retrieve values from:
    ```python
    [
        'V', 'I', 'P', 'CE', 'SOC', 'Alarm',
        'AR', 'Relay', 'H2', 'H17', 'H18'
    ]
    ```
- Every 2 seconds, retrieve values from:
    ```python
    [
        'TTG', 'H1', 'H3', 'H4', 'H5'
    ]
    ```
- Every 5 seconds, retrieve values from:
    ```python
    [
        'H6', 'H7', 'H8', 'H9', 'H10'
    ]
    ```
- Every 10 seconds, retrieve values from:
    ```python
    [
        'H11', 'H12', 'H13', 'H14', 'H15', 'H16'
    ]
    ```

The data will then be sent to the EmonCms Server. For more details, see the [Emoncms worker extra package](https://github.com/vemonitor/emon_worker_m8).

#### Running the Application

To run the `BatteryMonitor` app block:  
```
python vemonitor_m8 --block BatteryMonitor --debug
```

To run the `BatteryAndPannelsMonitor` app block: 
```
python vemonitor_m8 --block BatteryAndPannelsMonitor --debug
```
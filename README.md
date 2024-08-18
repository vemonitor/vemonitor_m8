# VeMonitor_m8

![CI](https://github.com/vemonitor/vemonitor_m8/actions/workflows/python-package.yml/badge.svg?branch=main)
[![PyPI package](https://img.shields.io/pypi/v/vemonitor_m8.svg)](https://pypi.org/project/vemonitor_m8/)
[![codecov](https://codecov.io/gh/vemonitor/vemonitor_m8/graph/badge.svg?token=M7VgGzkApi)](https://codecov.io/gh/vemonitor/vemonitor_m8)
[![Downloads](https://static.pepy.tech/badge/vemonitor_m8)](https://pepy.tech/project/vemonitor_m8)

> **Note**
> This repository is under active development and is not yet fully tested.

> **Warning**
> Install and use this package at your own risk. 
> Misconfiguration or bugs in this application can result 
> in an abnormal quantity of disk read/writes and/or 
> requests to designated servers (e.g., the EmonCms Server).
> Ensure you fully understand and control:
> - Your VeMonitor configuration file settings.
> - Your Redis server settings.

VeMonitor M8 is a Python library for monitoring data from the Serial Victron Energy VE.Direct text protocol and more. Currently, it supports sending data from any device using the Serial Victron Energy VE.Direct text protocol to EmonCms web application Server.

## Installation

To install directly from GitHub:
```
python3 -m pip install "git+https://github.com/vemonitor/vemonitor_m8"
```

To install from PypI :
```
python3 -m pip install vemonitor_m8
```
## Configuration files
To run this app, you need to provide some YAML configuration files. See the [sample configuration files](https://github.com/vemonitor/vemonitor_m8/tree/main/config_sample) to understand the overall structure.

All configuration files must be placed in one of the following directories:
On Linux/Unix:
- `/opt/vemonitor_m8/conf/` or
- `/opt/vemonitor/conf/` or
- `/${HOME}/.vemonitor` or  
On Windows:
- `/${HOME}/.vemonitor`


## Vedirect to EmonCms
The library reads data from the Serial VE.Direct text protocol and writes the defined data at a specified interval to the [EmonCms](https://emoncms.org/) web application.

> Note: You need to install the [Emoncms worker extra package](https://github.com/vemonitor/emon_worker_m8).
```
pip install emon_worker_m8
```
If you want to install and run EmonCms locally, see the [EmonCms repository](https://github.com/emoncms/emoncms).

### Configuration Files
> See the [sample configuration files](https://github.com/vemonitor/vemonitor_m8/tree/main/config_sample/vedirect_to_emoncms)

You can copy these configuration files directly to your own configuration directory and then update the necessary settings.

### Run Vemonitor
First, you need to install any additional worker packages you require.

Next, set up your configuration files in your configuration directory.

#### How it works
In the [main sample configuration file](https://github.com/vemonitor/vemonitor_m8/blob/main/config_sample/vedirect_to_emoncms/vm_conf.yaml) `vm_conf.yaml`, there are two different AppBlocks:
- `BatteryMonitor`
- `BatteryAndPannelsMonitor`

For example, we can run BatteryMonitor for testing purposes.

From the configuration settings, this app will read data from the VE.Direct Serial Device bmv700, and the data will be cached on the local Redis server:
- Every second get values from:
```python
[
    'V', 'I', 'P', 'CE', 'SOC', 'Alarm',
    'AR', 'Relay','H2', 'H17', 'H18'
]
```
- Every 2 seconds get values from:
```python
[
    'TTG', 'H1', 'H3', 'H4', 'H5'
]
```
- Every 5 seconds get values from:
```python
[
    'H6', 'H7', 'H8', 'H9', 'H10'
]
```
- Every 10 seconds get values from:
```python
[
    'H11', 'H12', 'H13', 'H14', 'H15', 'H16'
]
```

Then the data will be sent to the EmonCms Server. See the [Emoncms worker extra package](https://github.com/vemonitor/emon_worker_m8) for more details.

#### Run 
To run `BatteryMonitor` app block:  
```
python vemonitor_m8 --block BatteryMonitor --debug
```

To run `BatteryAndPannelsMonitor` app block:  
```
python vemonitor_m8 --block BatteryAndPannelsMonitor --debug
```

Be aware, install and use this package at your own risks.
Missconfiguration or bug in this app can produce anormal quantity of:
- disk read/writes and/or
- requests on determined servers(Here EmonCms Server)
Be sure control and understant:
- your vemonitor configuration files settings,
- your Redis server settings.

# VeMonitor_m8

![CI](https://github.com/vemonitor/vemonitor_m8/actions/workflows/python-package.yml/badge.svg?branch=main)
[![PyPI package](https://img.shields.io/pypi/v/vemonitor_m8.svg)](https://pypi.org/project/vemonitor_m8/)
[![codecov](https://codecov.io/gh/vemonitor/vemonitor_m8/graph/badge.svg?token=M7VgGzkApi)](https://codecov.io/gh/vemonitor/vemonitor_m8)
[![Downloads](https://static.pepy.tech/badge/vemonitor_m8)](https://pepy.tech/project/vemonitor_m8)

> **Note**
> This repository is under active development and is not yet fully tested.

The `vemonitor_m8` package is a powerful and flexible framework designed for real-time monitoring and data acquisition from various energy systems and devices. It serves as an all-in-one solution to gather, process, and distribute data across multiple platforms, supporting diverse protocols and data sources such as VE.Direct, Redis, and EmonCms.

With `vemonitor_m8`, users can easily configure and manage connections to different devices and servers, enabling seamless data flow from energy meters, battery monitors, solar charge controllers, and other compatible equipment. The package is highly customizable, allowing you to set up different workers, connectors, and data processing pipelines tailored to your specific needs.

Key features of vemonitor_m8 include:

. **Versatile Data Integration**: Supports various input and output protocols, enabling data collection from multiple sources and distributing it to multiple destinations.
. **Modular Architecture**: The package is built around a modular design, making it easy to extend functionality with additional workers and connectors.
. **Real-Time Monitoring**: Enables real-time data monitoring, ensuring up-to-date insights into your energy systems.
. **Customizable Configuration**: Offers flexible configuration options to suit a wide range of use cases, from simple home setups to complex industrial applications.

Whether you are looking to monitor a single device or manage a large network of energy systems, vemonitor_m8 provides the tools and flexibility to build a robust and efficient monitoring solution.

> **Warning**  
> Use this package at your own risk. Misconfiguration or bugs in this application can lead to an excessive number of disk read/writes and/or requests to designated servers (e.g., the EmonCms Server). It is essential that you fully understand and manage:
> - Your VeMonitor configuration file settings.
> - Your Redis server settings.  
> 

> **Warning**  
> It is strongly recommended to test your configuration using a monitoring tool like Telegraf/Grafana and Redis/Grafana to supervise and control disk read/writes and HTTP requests, ensuring they follow expected patterns.

It currently supports:
- Reading and formatting data from:
    - Any device using the Serial Victron Energy VE.Direct text protocol
- Sending the compiled and formatted data to:
    - Redis Server
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

## Interfacers (Workers)

By default `vemonitor_m8` includes two primary workers, or interfacers, by default. Additionally, you can install optional external workers as Python packages to extend functionality.

### VE.Direct Worker

The `vedirect` worker is a versatile component of the `vemonitor_m8` package, designed to facilitate communication with devices using the VE.Direct text protocol over a serial connection. Primarily functioning as an Input Worker API, it allows for the seamless reading of data from a variety of Victron Energy devices, such as battery monitors and solar charge controllers.

For detailed instructions on configuring and utilizing the `vedirect` worker, please refer to the [**VeDirect Worker documentation**](https://github.com/vemonitor/vemonitor_m8/tree/main/vemonitor_m8/workers/vedirect/README.md).

#### Basic Example of appConnectors Configuration

Below is an example configuration for establishing a connection with a device using the serial VE.Direct text protocol, defined within the `appConnectors` settings:

```yaml
appConnectors:
    # Serial appConnectors settings
    # Used to establish connections to devices using the serial VE.Direct text protocol
    serial:
        # Device source name (Defined by user)
        # str: Alphanumeric characters, '-' and/or '_'
        bmv700:
            # Path of the serial port
            # -> Required if no serialTest setting is present
            serialPort: '/dev/ttyACM2'
            # Serial test to determine if the serial data corresponds with this serial item.
            # -> Useful if more than one serial item is read, or if the serial port changes.
            # -> E.g., changing the USB port, where the serial port name is not updated by the user.
            # -> Scans all serial ports on serial paths ['/dev', '/${HOME}', ...] and searches for the corresponding serial.
            serialTest:
                # Test name (Defined by user)
                # str: Required, Alphanumeric characters, '-' and/or '_'
                PIDTest:
                    # Type of test to execute
                    # str: Required, 'value' or 'columns'
                    typeTest: "value"
                    # The block key name to compare
                    # str: Required, Alphanumeric characters, '-' and/or '_'
                    key: "PID"
                    # The block key value to compare
                    # The value needs to be equal to the serial output to pass the test
                    # str: Required, Alphanumeric characters, '-' and/or '_'
                    value: "0x203"
```

#### Basic Example of appBlock Configuration

Below is a basic example of how to configure the VeDirect worker within the `appBlock` settings:

```yaml
appBlocks:
    -   # Block item name (must be unique)
        name: "VedirectToRedis"
        # (...)
        inputs:
            # Serial input worker reads data from the serial device
            serial:
                -   # Input block item name
                    # Used to identify block items
                    # str: Required, Alphanumeric characters, '-' and/or '_'
                    name: "bmv700"
                    # AppConnector source name to connect
                    # Must correspond to one of the serial appConnectors defined above
                    # str: Required, Alphanumeric characters, '-' and/or '_'
                    source: "bmv700"
                    # Read time interval (in seconds)
                    # int: Required, positive number
                    time_interval: 1
                    # Device type name (Defined by user)
                    # str: Required, Alphanumeric characters, '-' and/or '_'
                    device: "BMV"
                    # Reference columns for standardizing block names
                    # To be processed by vemonitor_m8 middlewares 
                    ref_cols: [
                        ['bat_voltage', 'V'],
                        ['bat_current', 'I'],
                        ['bat_power', 'P'],
                        ['bat_temperature', 't_bat'],
                        ['loc_temperature', 't_int']
                    ]
                    # Node columns to read from the serial device
                    # Contains block column names to extract from serial packets read
                    columns: [
                        'V', 'I', 'P', 'CE', 'SOC', 'Alarm',
                        'AR', 'Relay', 'H2', 'H17', 'H18'
                    ]
```

### redis Worker

The `redis` worker is designed to handle both reading from and writing to Redis servers. It functions as an Input/Output Interfacer API, facilitating the transfer of data between the vemonitor_m8 package and one or more Redis servers.


For detailed instructions on how to use the Redis worker, please refer to the [**Redis Worker documentation**](https://github.com/vemonitor/vemonitor_m8/tree/main/vemonitor_m8/workers/redis/README.md).

#### Use local Redis Server
To use a local Redis server, you'll need to install it on your system or use an appropriate Docker image. For detailed instructions, refer to the [**Official Redis documentation**](https://redis.io/docs/latest/get-started/).


#### Basic Example of appConnectors Configuration

Below is an example configuration for connecting to Redis servers using the `appConnectors` settings:

```yaml
appConnectors:
    # Redis appConnectors settings
    # Used to establish connections to Redis servers
    redis:
        # Source name of Redis Server
        # Defined by the user
        # str: Alphanumeric characters, '-' and/or '_'
        local:
            # Server host IP address
            # str: required
            host: "127.0.0.1"
            # Server port number
            # int: required
            port: 6379
        # Source name of Redis Server
        # Defined by the user
        # str: Alphanumeric characters, '-' and/or '_'
        remote:
            # Server host IP address
            # str: required
            host: "192.168.0.52"
            # Server port number
            # int: required
            port: 16379
            # Server password
            # str: Optional
            password: "REDIS_SERVER_PASSWORD"
```

#### Basic Example of appBlock Configuration

Here’s a basic example of how to configure the Redis worker in the `appBlock` settings:

```yaml
outputs:
    # Redis output worker writes data to the Redis server
    redis:
        - # Redis server source configuration name
          # Refer to the appConnectors Redis item with the source set as "local"
          source: "local"
          # Redis storage structure
          # In this example, the Redis HmapTimeSeries module is selected
          redis_data_structure: "HmapTimeSeries"
          # Data write interval
          time_interval: 1
          # Data cache interval
          # This value, combined with time_interval,
          # determines how many points are sent simultaneously to the server.
          # Total points = time_interval * cache_interval
          # Example: Total points = 1 * 5 = 5
          # Meaning every 5 seconds, 5 points are sent per node determined by the columns key
          cache_interval: 5
          # Redis node (must be unique)
          # Used as the Set key to store nodes from columns
          redis_node: "bat_bmv700"
          # Reference columns for standardizing block names
          # To be processed by vemonitor_m8 middleware
          ref_cols:  [
              ['bat_voltage', 'V'],
              ['bat_current', 'I'],
              ['bat_power', 'P']
          ]
          # Node columns to store in the Redis server
          columns: 
              # Key: hMap node name
              # Values: column block names to extract from the data read
              bmv700: [
                  'V', 'I', 'P', 'SOC', 'Alarm',
                  'AR', 'Relay'
              ]
```

### EmonCms Worker
The `EmonCms` worker is external python package [`emon_worker_m8`](https://github.com/vemonitor/emon_worker_m8).
It acts as an Output Interfacer API, tasked with sending data to an EmonCms web application.

To use it you need to install the package first:
```
pip install emon_worker_m8
```
> **Warning**:
> Try to ever maintain packages up to date.
> ```yaml
> pip install --update vemonitor_m8 emon_worker_m8
> ```

Then refer to the `emon_worker_m8` documentation file for how to use it.

> **Note**  
> If you want to install and run EmonCms locally,  
> see the [EmonCms repository](https://github.com/emoncms/emoncms).

#### Basic Example of appConnectors Configuration

Below is an example configuration for connecting to EmonCms servers using the `appConnectors` settings:

```yaml
appConnectors:
    # EmonCms appConnectors settings
    # Used to establish connections to EmonCms servers
    emoncms:
        # Source name of the EmonCms Server
        # Defined by the user
        # str: Alphanumeric characters, '-' and/or '_'
        local:
            # Base HTTP address and port of the EmonCms Server
            # str: required
            addr: "http://127.0.0.1:8080"
            # EmonCms Server API Key
            # Must have write permissions to work properly
            # str: required
            apikey: "EMONCMS_API_KEY"
```

This example demonstrates how to configure an `appConnectors` entry for connecting to a local EmonCms server, including setting the server address and API key with write permissions.

#### Basic Example of appBlock Configuration

Here’s a basic example of how to configure the `emon_worker_m8` worker in the `appBlock` settings:
```yaml
    outputs:
        emoncms:
            -   name: "bat_t1"
                source: "local"
                columns:
                    bmv700: [
                        'V', 'I', 'P', 'CE', 'SOC', 'Alarm',
                        'AR', 'Relay','H2', 'H17', 'H18', 'time_ref'
                    ]
                time_interval: 1
                cache_interval: 10 # number of items to send at same time
```

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
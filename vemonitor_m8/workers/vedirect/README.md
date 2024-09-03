# VeDirect Worker modules

## Overview

The VeDirect worker module in the vemonitor_m8 package is designed to interface with devices using the Victron Energy VE.Direct text protocol. This module enables the reading and processing of data from devices such as battery monitors and charge controllers, facilitating seamless integration with Redis servers and other output interfaces.

# Key Features

. **Direct Serial Communication**: The worker reads data from devices connected via serial ports using the VE.Direct text protocol.
. **Configurable Data Mapping**: Supports flexible configuration for mapping incoming data to standardized fields.
. **Serial Port Auto-Detection**: Includes a serial port test feature to automatically detect and select the correct serial port based on device output.

## Configuration

o work with data from the VE.Direct text protocol in the `vemonitor_m8` package, certain settings must be configured within the Inputs/Outputs block items and `appConnectors`.

### appConnector

To connect a worker to a device using the VE.Direct text protocol over a serial connection, you need to define the serial settings in the `appConnectors` configuration.

Here’s a basic example of the required configuration:
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

### Input Worker

To read data from a device using the VE.Direct text protocol over a serial connection, you can set up a `serial` input block item in the main configuration file as follows:

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
# Redis Worker modules

The Redis Worker Modules are integral components of the vemonitor_m8 package, enabling efficient data handling and storage using Redis as the backend. These modules facilitate the seamless integration of Victron Energy devices, such as MPPT solar charge controllers and battery monitors, with a Redis server, ensuring real-time data processing and storage.

## Overview

Redis Worker Modules are designed to streamline the interaction between the `vemonitor_m8` package and Redis. By leveraging Redis' high-performance data structures, these modules allow you to efficiently read and write data from and to the Redis server, ensuring that your energy monitoring system operates smoothly and reliably.

Whether you're collecting data from a variety of inputs or outputting processed data for further analysis, the Redis Worker Modules provide a flexible and robust solution tailored to the needs of energy monitoring systems.

# Key Features
. **Configurable Data Structures**: Choose from multiple data storage structures, such as Hmap Time Series, to best suit your application's needs.
. **Efficient Data Handling**: Handle large volumes of data with ease, ensuring timely and accurate data storage.
. **Flexible Configuration**: Customize input and output workers to connect with Redis, adapting to a variety of use cases.
. **Real-Time Processing**: Ensure that data is processed and stored in real-time, facilitating up-to-date monitoring and analysis.

## Configuration

To work with Redis in the `vemonitor_m8` package, you need to configure certain settings within the Inputs/Outputs block items.

### appConnector

To connect an interfacer or worker to a redis server you need define redis server settings on appConnectors configuration.

Here’s a basic example of the required configuration:
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
### Input Worker

> **Warning**
> At this time Redis Input worker is not available.
> And do nothing 

To read data from Redis, you can set up a Redis input block item in the main configuration file as follows:

```yaml
    -   # Block item name (must be unique)
        name: "VedirectToRedis"
        # (...)
        inputs:
            # Redis input worker reads data from the Redis server
            redis:
              - # Input item name (must be unique)
                name: "external_data"
                # Redis server source configuration name
                # See appConnectors Redis item with the source set as "local"
                source: "local"
                # Redis storage structure
                # Here, the Redis HmapTimeSeries module is selected
                redis_data_structure: "HmapTimeSeries"
                # Read time interval
                time_interval: 1
                # Redis node (must be unique)
                # Used as the Set key to store nodes from columns
                redis_node: "bat_bmv700"
                # Reference columns for standardizing block names
                # To be processed by vemonitor_m8 middlewares
                ref_cols:  [
                    ['bat_voltage', 'V'],
                    ['bat_current', 'I'],
                    ['bat_power', 'P']
                ]
                # Node columns to read from the Redis server
                columns: 
                    # Key: hMap node name
                    # Values: column block names to extract from the data read
                    bmv700: [
                        'V', 'I', 'P', 'SOC', 'Alarm',
                        'AR', 'Relay'
                    ]
```

### Output Worker

To store data in Redis, you can set up a Redis output block item in the main configuration file as follows:

```yaml
    -   # Block item name (must be unique)
        name: "VedirectToRedis"
        # (...)
        inputs:
            "(...)"
        outputs:
            # Redis output worker writes data to the Redis server
            redis:
              - # Redis server source configuration name
                # See appConnectors Redis item with the source set as "local"
                source: "local"
                # Redis storage structure
                # Here, the Redis HmapTimeSeries module is selected
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
                # To be processed by vemonitor_m8 middlewares
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
## Data store types

These modules are designed to store data on a Redis server using various types of data structures.

### Hmap Time Series
This module stores time series data as hash maps (hMaps) and is the default storage type used by the `vemonitor_m8` package. In the Inputs/Outputs workers, you can specify `redis_data_structure`: `"HmapTimeSeries"` to select this storage structure or leave the setting blank to use the default.

On the Redis server, two kinds of data are stored.

#### Nodes store
For every input/output block item, nodes are stored in a set using the  `redis_node` value as the set's key name. 

Node storage example:
> See the Redis input/output block item configuration examples below:
```python
    "bat_bmv700": ["bmv700"]
```

#### Time series store
For each column node, data time series are stored in a hash map (hMap). The hMap's name is a combination of the `columns` node name, prefixed by the `redis_node` value. Each key in the hMap represents a timestamp, and the corresponding value is a JSON-formatted dictionary containing the `columns` item values.

hMap Time Series storage example:
```python
    # Column node name prefixed by the redis_node value
    "bat_bmv700_bmv700": {
        '1725292361': '{"V": 12.064, "I": -7.52, "P": -91.0, "SOC": 83.8, "Alarm": 0, "AR": 0, "Relay": 0}',
        '1725292362': '{"V": 12.065, "I": -7.537, "P": -91.0, "SOC": 83.8, "Alarm": 0, "AR": 0, "Relay": 0}',
        '1725292363': '{"V": 12.064, "I": -7.537, "P": -91.0, "SOC": 83.8, "Alarm": 0, "AR": 0, "Relay": 0}',
        '1725292364': '{"V": 12.064, "I": -7.514, "P": -91.0, "SOC": 83.8, "Alarm": 0, "AR": 0, "Relay": 0}',
        '1725292365': '{"V": 12.064, "I": -7.536, "P": -91.0, "SOC": 83.8, "Alarm": 0, "AR": 0, "Relay": 0}'
    }
```

#### Example
For instance, if we configure the output block as follows:
```yaml
    outputs:
        # Redis output worker writes data to the Redis server
        redis:
            - # Redis server source configuration name
            # See appConnectors Redis item with the source set as "local"
            source: "local"
            # Redis storage structure
            # Here, the Redis HmapTimeSeries module is selected
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
            # Node columns to store in the Redis server
            columns: 
                # Key: hMap node name
                # Values: column block names to extract from the data read
                bmv700: [
                    'V', 'I', 'P', 'SOC', 'Alarm',
                    'AR', 'Relay'
                ]
```

In this example nodes are stored as: 
- The `redis_node` value is `bat_bmv700`
- The `columns` key contain only one node `bmv700`

This produces the following node store:
```python
    "bat_bmv700": ["bmv700"]
```

The hMap Time Series store would be as follows:
- The `redis_node` value is `bat_bmv700`
- The `columns` key contain only one node `bmv700`
- Data is sent every five seconds.
  Example: `time_interval` x `cache_interval` = `send_interval`
  => 1  x  5 = 5
  This means five time series points containing one node of columns items are sent every five seconds.

That produces an hMap like this:
```python
    # Column node name prefixed by the redis_node value
    "bat_bmv700_bmv700": {
        '1725292361': '{"V": 12.064, "I": -7.52, "P": -91.0, "SOC": 83.8, "Alarm": 0, "AR": 0, "Relay": 0}',
        '1725292362': '{"V": 12.065, "I": -7.537, "P": -91.0, "SOC": 83.8, "Alarm": 0, "AR": 0, "Relay": 0}',
        '1725292363': '{"V": 12.064, "I": -7.537, "P": -91.0, "SOC": 83.8, "Alarm": 0, "AR": 0, "Relay": 0}',
        '1725292364': '{"V": 12.064, "I": -7.514, "P": -91.0, "SOC": 83.8, "Alarm": 0, "AR": 0, "Relay": 0}',
        '1725292365': '{"V": 12.064, "I": -7.536, "P": -91.0, "SOC": 83.8, "Alarm": 0, "AR": 0, "Relay": 0}'
    }
```
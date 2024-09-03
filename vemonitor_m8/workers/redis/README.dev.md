# Redis worker modules

## RedisCli

ToDo: 
- Redis current data base must be defined and not set to default.
- Reference data must be added to identify `vemonitor_m8` data bases structures.
- Before writing selected db must be analysed to ensure writing source,  
  to avoid write in a existent db used by another process.


## HmapTimeSeriesApp

ToDo: 
- `redis_node` configuration value need to be affected to `self.node_base` in `HmapTimeSeriesApp` class. Used to prefix hMap nodes names to avoid data colisions with `columns` node names on different block items.
- nodes names and keys values need to be validated.
- cache data must be validated
- use pipelines in loops with redis server requests
- columns items names must be updated by `ref_cols` setting values
- achieve unnit test class and simplify the code
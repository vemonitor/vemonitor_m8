# Redis worker modules

## RedisCli

ToDo: 
- Redis current data base must be defined and not set to default.
- Reference data must be added to identify `vemonitor_m8` data bases structures.
- Before writing selected db must be analysed to ensure writing source,  
  to avoid write in a existent db used by another process.


## HmapTimeSeriesApp

ToDo: 
- nodes names and keys values need to be validated.
- cache data must be validated
- columns items names must be updated by `ref_cols` setting values
- achieve unnit test class and simplify the code
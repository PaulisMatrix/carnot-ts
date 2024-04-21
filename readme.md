# Carnot - Device stats timeseries analysis

* Device metrics analysis using Redis with an API built on top of it.

* The metrics collected look something like this:

    ```
    id      latitute    longitude   sts(timestamp)        speed
    25029   27.8779583  76.06095886 2021-10-23T14:08:02Z    0
    25029   27.8779583  76.06095886 2021-10-23T14:08:06Z    0
    25029   27.8779583  76.06095886 2021-10-23T14:08:04Z    0
    25029   27.8779583  76.06095886 2021-10-23T14:08:00Z    0
    25029   27.8779583  76.06095886 2021-10-23T14:07:56Z    0
    25029   27.8779583  76.06095886 2021-10-23T14:07:58Z    7
    25029   27.8779583  76.06095886 2021-10-23T14:07:50Z    7
    25029   27.8779583  76.06095886 2021-10-23T14:07:54Z    8
    25029   27.8779583  76.06095886 2021-10-23T14:07:52Z    2
    25029   27.8779583  76.06095886 2021-10-23T14:07:46Z    1
    ```

* Requirements:

    *   An API that takes device ID and returns device’s latest information in response.

        `http://localhost:3001/devices/6888.0/latest-info/`

    *   An API that takes device ID and returns start location & end location for that device.
        Location should be (lat, lon) tuple.

        `http://localhost:3001/devices/6888.0/distance-travelled/`
    
    *   An API that takes in device ID, start time & end time and returns all the location
        points as list of latitude, longitude & time stamp.

        `http://localhost:3001/devices/6888.0/locations/?iso_start_time=2021-10-23T18:00:54Z&iso_end_time=2021-10-23T19:59:36Z&page_size=10&page_number=1`

* Analysis steps:

    * Load the csv into a pandas dataframe first and sort by column(sts)

    * Batch the data points say around 20 records in a single batch and write the aggregted data point instead.
    
    * Take that result and dump into redis sorted sets so that we have stats in increasing order of timestamps and can efficiently query for start, end, latest timestamps. They key would be of the following form:

        `ZADD 25029 <batched_timestamp1> "lat1:long1,speed2,timestamp2"`

        `ZADD 25029 <batched_timestamp2> "lat2:long2,speed2,timestamp2"`
    
    * Can query for the different APIs like this:

        `ZRANGEBYSCORE 25029 start_timestamp end_timestamp`

        since its a sorted set, first index will be min_timestamp, last index will be max_timestamp
    
    * Use FastAPI for the server having the corresponding endpoints.

* Docs can be accessed here: `http://0.0.0.0:3001/docs` or `http://0.0.0.0:3001/redoc`

* Detailed project walkthrough: https://drive.google.com/file/d/1IRww06QAFzZx-vz6cfDbYIWOT6aN5uUD/view



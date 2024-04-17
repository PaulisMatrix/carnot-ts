# Carnot - Device stats timeseries analysis

* Device metrics analysis using Redis with an API built on top of it.

* The metrics collected look something like this:

    id      latitute    longitude   sts(timestamp)        speed
    ```
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

    * An API that takes device ID and returns device’s latest information in response.

    * An API that takes device ID and returns start location & end location for that device.
        Location should be (lat, lon) tuple.
    
    * An API that takes in device ID, start time & end time and returns all the location
        points as list of latitude, longitude & time stamp.

* Analysis steps:

    * Load the csv into a pandas dataframe first and sort by column(sts)

    * Iterate over each row/datapoint for a particular device_id and batch the records until when the time difference between the first_timestamp and the current_timestamp is >=3 secs. Avg out latitute, longitude, speed.
    
    * Take that result and dump into redis sorted sets so that we have stats in increasing order of timestamps and can efficiently query for start, end, latest timestamps. They key would be of the following form:

        `ZADD 25029 <batched_timestamp1> "lat1:long1,speed2,timestamp2"`

        `ZADD 25029 <batched_timestamp2> "lat2:long2,speed2,timestamp2"`
    
    * Can query for the different APIs like this:

        `ZRANGEBYSCORE 25029 start_timestamp end_timestamp`

        since its a sorted set, one index will be min_timestamp, last index will be max_timestamp
    
    * Use FastAPI for the server having the corresponding endpoints.

* TODO:

    1. Modify redis_client to add all commands related to redis sorted sets

    2. Loan, Extract, Transform the csv device metrics into a pandas dataframe and write to redis.

    3. Define data models and add relevant endpoints to the FASTAPI server.

    4. Add relevant functionality to the corresponding endpoints.

    5. Testing and Validation.

    6. Fin



# sdig
Helper Routines for reading ERDDAP DSG metadata.

All ERDDAP DSG data sets have a handy metadata construct located at server.gov/erddap/info/dataset_id/index.csv. If you read that metadata into a Pandas dataframe
as in info_df = pd.read_csv(info_url), then you can use the methods here to extract lots of interesting things as detailed below.

**NAME**

    sdig.erddap.info

**FUNCTIONS**
```
    get_depths(depth_name, url)
        Returns a list of depths read directly from an ERDDAP data source. Use dsg_info to get the name of the depth
        variable.

            Parameters:
                    :param: depth_name: A string which the ERDDAP/netCDF short variable name of the variable
                    that contains the DSG ID
                    :type: str
                    :param: url: data url of the tabledap data set from which to read the data values
                    :type: str

            Returns:
                    :returns: depths: a sorted list of distinct depths.
                    :rtype: list

    get_dsg_info(dsg_type, info_df)
        Returns the name of the Z variable as a string and the DSG ID of the data set as a dict
        with keys timeseries_id, profile_id, trajectory_id as appropriate.
        A timeseriesprofile data set has both a timeseries_id and a profile_id


        Parameters:
            :param: dsg_type: the dsg_type of the data set. Use get_dsg_type
            :type: str
            :param: info_df: A dataframe from the pd.read_csv(erddap.server.gov/erddap/info/DS_ID/index.csv)
            :type: pd.DataFrame
        Returns:
            :returns: depth_name: the value of the title global attribute
            :rtype: str
            :returns: dsg_id: the variable names of the id variables as values with [dsg_type]_id as keys
            :rtype: str

    get_dsg_type(info_df)
        Returns the dsg_type of the data set. One of timeseries, profile, trajectory, timeseriesprofile.

        Parameters:
            :param: info_df: A dataframe from the pd.read_csv(erddap.server.gov/erddap/info/DS_ID/index.csv)
            :type: pd.DataFrame
        Returns:
            :returns: dsg_type: the dsg type as a lower case string
            :rtype: str

    get_info_url(data_url)
        Returns the info CSV URL from the data URL of a DSG ERDDAP dataset. Changes:
         https://data.pmel.noaa.gov/pmel/erddap/tabledap/CGBN_Canada.html or
         https://data.pmel.noaa.gov/pmel/erddap/tabledap/CGBN_Canada
         to
         https://data.pmel.noaa.gov/pmel/erddap/info/CGBN_Canada/index.csv

        :param data_url:
        :type: str
        :return: The info CSV url for use with the
        :rtype: str

    get_time_marks(start, end)
        Make some time marks for the time slider, only one mark at the beginning and one mark at the end

        Parameters:
            :param: start: start time as Unix epoch seconds
            :type: float
            :param: end: end time as Unix epoch seconds
            :type: float

        Returns:
            :returns: marks: the marks as suitable for input into the slider DASH widget
            :rtype: dict

    get_times(info_df)
        Returns a tuple of start time and end times both as YYYY-MM-dd string as Unix epoch seconds read from the metadata
        not the actual data values so it should be fast

        Parameters:
                :param: info_df: A dataframe from the pd.read_csv(erddap.server.gov/erddap/info/DS_ID/index.csv)
                :type: pd.DataFrame

        Returns:
                :returns: start_date: start date formatted YYYY-MM-dd
                :rtype: str
                :returns: end_date: end date formtted YYYY-MM-dd
                :rtype: str
                :returns: start_date_second: the start date as seconds from the Unix epoch
                :rtype: float
                :returns: end_date_seconds: the end date as seconds from the Unix epoch
                :rtype: float

    get_title(info_df)
        Returns the value of the title global attribute of the data set.

        Parameters:
            :param: info_df: A dataframe from the pd.read_csv(erddap.server.gov/erddap/info/DS_ID/index.csv)
            :type: pd.DataFrame

        Returns:
            :returns: title: the value of the title global attribute
            :rtype: str

    get_variables(info_df)
        Returns a tuple list and dictionaries describing the data variables in an ERDDAP data set. Check if the key
        is in the dict before use because not all variables have long_name, units and standard_name attributes.

        Parameters:
                :param: info_df: A dataframe from the pd.read_csv(erddap.server.gov/erddap/info/DS_ID/index.csv)
                :type: pd.DataFrame

        Returns:
                :returns: variables: the short variable names as a string
                :rtype: list
                :returns: long_names: a dict of variable long names values with the short names as the keys
                :rtype: dict
                :returns: units: a dict of variable units values with the short names as the keys
                :rtype: dict
                :returns: standard_names: a dict of variable standard_name values with the short names as the keys
                :rtype: dict

    make_platform_constraint(dsg_id_var, in_platforms)
        Returns a ERDDAP formatted 'OR' constraint that will allow selection of rows which contain any of the
        ID's in the input.

            Parameters:
                    :param: dsg_id_var: A string which the ERDDAP/netCDF short variable name of the variable that contains
                    :type: str
                    :param: in_platforms: DASH returns either a str or a list of str which you can pass into this method
                    directly to get the constraint string
                    :type: list or str
            Returns:
                    :returns: return_stuff: a dictionary 'con' has the constraint, and 'platforms' is the list of platforms
                    as a list even if the input was a str variable. Use dsg_info to get the dsg_id_var name.
                    :rtype: dict
```

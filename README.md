# sdig
Helper Routines for reading ERDDAP DSG metadata.

## Installation (for the time being)

pip install git+https://github.com/noaaroland/sdig.git

**Quick start example:**
```
from sdig.erddap.info import Info
myinfo = Info('https://data.pmel.noaa.gov/pmel/erddap/tabledap/weatherpak_m2.html')
print(myinfo.get_title())
```
```
EcoFOCI M2 surface mooring weather data
```

N.B. @classmethods are invoked like this:
```
info_url = Info.get_info_url('https://data.pmel.noaa.gov/pmel/erddap/tabledap/weatherpak_m2.html')
print(info_url)
```
```
https://data.pmel.noaa.gov/pmel/erddap/info/weatherpak_m2/index.csv
```

## Details

All ERDDAP DSG data sets have a handy metadata construct located at server.gov/erddap/info/dataset_id/index.csv. The sdgi.erddap.info.Info object gives you access to the metadata in a way that lets you know what data are there, what time it covers and what type of discrete geomertry structure it has.


**METHODS**
```
def get_dsg_type(self):
        """
        Returns the dsg_type of the data set. One of timeseries, profile, trajectory, timeseriesprofile.

        Returns:
            :returns: dsg_type: the dsg type as a lower case string
            :rtype: str
        """

    def get_dsg_info(self):
        """
        Returns the name of the Z variable as a string and the DSG ID of the data set as a dict
        with keys timeseries, profile, trajectory as appropriate.
        A timeseriesprofile data set has both a timeseries and a profile

        Returns:
            :returns: depth_name: the value of the title global attribute
            :rtype: str
            :returns: dsg_id: the variable names of the id variables as values with [dsg_type] as keys
            :rtype: str
    
        """


    def get_depths(self):
        """
        Returns a list of depths read directly from an ERDDAP data source.

            Returns:
                    :returns: depths: a sorted list of distinct depths.
                    :rtype: list
        """
    
    def get_times(self):
        """
        Returns a tuple of start time and end times both as YYYY-MM-dd string as Unix epoch seconds read from the metadata
        not the actual data values so it should be fast
    
        Returns:
                :returns: start_date: start date formatted YYYY-MM-dd
                :rtype: str
                :returns: end_date: end date formtted YYYY-MM-dd
                :rtype: str
                :returns: start_date_second: the start date as seconds from the Unix epoch
                :rtype: float
                :returns: end_date_seconds: the end date as seconds from the Unix epoch
                :rtype: float
        """


    def get_variables(self):
        """
        Returns a tuple list and dictionaries describing the data variables in an ERDDAP data set. Check if the key
        is in the dict before use because not all variables have long_name, units and standard_name attributes.
    
        Returns:
                :returns: variables: the short variable names as a string
                :rtype: list
                :returns: long_names: a dict of variable long names values with the short names as the keys
                :rtype: dict
                :returns: units: a dict of variable units values with the short names as the keys
                :rtype: dict
                :returns: standard_names: a dict of variable standard_name values with the short names as the keys
                :rtype: dict
        """


    def get_title(self):
        """
        Returns the value of the title global attribute of the data set.

        Returns:
            :returns: title: the value of the title global attribute
            :rtype: str
    
        """


    @classmethod
    def make_platform_constraint(cls, dsg_id_var, in_platforms):
        """
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
        """

    @classmethod
    def get_time_marks(cls, start, end):
        """
        Make some time marks for the time slider, only one mark at the beginning and one mark at the end

        Parameters:
            :param: start: start time as Unix epoch seconds
            :type: float
            :param: end: end time as Unix epoch seconds
            :type: float

        Returns:
            :returns: marks: the marks as suitable for input into the slider DASH widget
            :rtype: dict
        """

    @classmethod
    def get_info_url(cls, data_url):
        """
        Returns the info CSV URL from the data URL of a DSG ERDDAP dataset. Changes:
        https://data.pmel.noaa.gov/pmel/erddap/tabledap/CGBN_Canada.html or
        https://data.pmel.noaa.gov/pmel/erddap/tabledap/CGBN_Canada
        to
        https://data.pmel.noaa.gov/pmel/erddap/info/CGBN_Canada/index.csv

        :param data_url:
        :type: str
        :return: The info CSV url for use with the
        :rtype: str
        """
```

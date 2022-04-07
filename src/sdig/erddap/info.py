import pandas as pd
import datetime
import dateutil.parser
import re


def get_info_url(data_url):
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
    if data_url.endswith('/index.csv'):
        return data_url
    if data_url.endswith('.html'):
        data_url = re.sub('\\.html$', '', data_url)
    data_url = data_url.replace('tabledap', "info")
    data_url = data_url + '/index.csv'
    return data_url


def make_platform_constraint(dsg_id_var, in_platforms):
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
    con = ''
    p_list = []
    if in_platforms is not None:
        if isinstance(in_platforms, list):
            in_platforms = [str(p) for p in in_platforms]
            p_list = in_platforms
            if len(in_platforms) > 1:
                con = dsg_id_var + '=~"' + '|'.join(in_platforms) + '"'
            elif len(in_platforms) == 1:
                con = dsg_id_var + '="' + in_platforms[0] + '"'
        else:
            con = dsg_id_var + '="' + str(in_platforms) + '"'
            p_list = [str(in_platforms)]
    return {'con': con, 'platforms': p_list}


def get_depths(depth_name, url):
    """
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
    """
    depth_url = url + '.csv?' + depth_name + '&distinct()&orderBy("' + depth_name + '")'
    depth_df = pd.read_csv(depth_url, skiprows=[1])
    depths = depth_df[depth_name].to_list()
    return depths


def get_times(info_df):
    """
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
    """
    chk_start_date = info_df.loc[
        (info_df['Row Type'] == 'attribute') & (info_df['Attribute Name'] == 'time_coverage_start') & (
                info_df['Variable Name'] == 'NC_GLOBAL')]['Value'].to_list()[0]

    chk_end_date = info_df.loc[
        (info_df['Row Type'] == 'attribute') & (info_df['Attribute Name'] == 'time_coverage_end') & (
                info_df['Variable Name'] == 'NC_GLOBAL')]['Value'].to_list()[0]

    start_date_datetime = dateutil.parser.isoparse(chk_start_date)
    end_date_datetime = dateutil.parser.isoparse(chk_end_date)

    start_date = start_date_datetime.date().strftime('%Y-%m-%d')
    end_date = end_date_datetime.date().strftime('%Y-%m-%d')

    start_date_seconds = start_date_datetime.timestamp()
    end_date_seconds = end_date_datetime.timestamp()
    return start_date, end_date, start_date_seconds, end_date_seconds


def get_variables(info_df):
    """
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
    """
    variables = list(info_df.loc[(info_df['Row Type'] == 'attribute') & (info_df['Variable Name'] != 'NC_GLOBAL')][
        'Variable Name'].unique())
    long_df_all = info_df.loc[(info_df['Row Type'] == 'attribute') & (info_df['Attribute Name'] == 'long_name')]
    long_df = long_df_all.drop_duplicates(subset=['Variable Name'])
    long_names = dict(zip(long_df['Variable Name'], long_df['Value'].str.capitalize()))
    unit_df = info_df.loc[(info_df['Row Type'] == 'attribute') & (info_df['Attribute Name'] == 'units')]
    units = dict(zip(unit_df['Variable Name'], unit_df['Value']))
    std_nme_all = info_df.loc[(info_df['Row Type'] == 'attribute') & (info_df['Attribute Name'] == 'standard_name')]
    std_nme_df = std_nme_all.drop_duplicates(subset=['Variable Name'])
    standard_names = dict(zip(std_nme_df['Variable Name'], std_nme_df['Value'].astype(str)))
    return variables, long_names, units, standard_names


def get_dsg_type(info_df):
    """
    Returns the dsg_type of the data set. One of timeseries, profile, trajectory, timeseriesprofile.

    Parameters:
        :param: info_df: A dataframe from the pd.read_csv(erddap.server.gov/erddap/info/DS_ID/index.csv)
        :type: pd.DataFrame
    Returns:
        :returns: dsg_type: the dsg type as a lower case string
        :rtype: str
    """
    dsg_type = list(info_df.loc[(info_df['Row Type'] == 'attribute') & (info_df['Variable Name'] == 'NC_GLOBAL') & (
                info_df['Attribute Name'] == 'cdm_data_type')]['Value'].unique())[0]
    dsg_type = dsg_type.lower()
    return dsg_type


def get_title(info_df):
    """
    Returns the value of the title global attribute of the data set.

    Parameters:
        :param: info_df: A dataframe from the pd.read_csv(erddap.server.gov/erddap/info/DS_ID/index.csv)
        :type: pd.DataFrame

    Returns:
        :returns: title: the value of the title global attribute
        :rtype: str

    """
    title = list(info_df.loc[(info_df['Row Type'] == 'attribute') & (info_df['Variable Name'] == 'NC_GLOBAL') & (
                info_df['Attribute Name'] == 'title')]['Value'].unique())[0]
    return title


def get_dsg_info(dsg_type, info_df):
    """
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

    """
    dsg_id = {}
    depth_name = None
    if dsg_type == 'timeseries':
        timeseries_id = list(info_df.loc[
            (info_df['Row Type'] == 'attribute') & (info_df['Value'] == 'timeseries_id') & (
                        info_df['Attribute Name'] == 'cf_role')]['Variable Name'].unique())[0]
        dsg_id['timeseries'] = timeseries_id
    elif dsg_type == 'trajectory':
        trajectory_id = list(info_df.loc[
            (info_df['Row Type'] == 'attribute') & (info_df['Value'] == 'trajectory_id') & (
                        info_df['Attribute Name'] == 'cf_role')]['Variable Name'].unique())[0]
        dsg_id['trajectory'] = trajectory_id
    elif dsg_type == 'profile':
        profile_id = list(info_df.loc[(info_df['Row Type'] == 'attribute') & (info_df['Value'] == 'profile_id') & (
                    info_df['Attribute Name'] == 'cf_role')]['Variable Name'].unique())[0]
        dsg_id['profile'] = profile_id
        depth_name = list(info_df.loc[(info_df['Row Type'] == 'attribute') & (info_df['Attribute Name'] == 'positive')][
            'Variable Name'].unique())[0]
    elif dsg_type == 'timeseriesprofile':
        profile_id = list(info_df.loc[(info_df['Row Type'] == 'attribute') & (info_df['Value'] == 'profile_id') & (
                    info_df['Attribute Name'] == 'cf_role')]['Variable Name'].unique())[0]
        dsg_id['profile'] = profile_id
        timeseries_id = list(info_df.loc[
            (info_df['Row Type'] == 'attribute') & (info_df['Value'] == 'timeseries_id') & (
                        info_df['Attribute Name'] == 'cf_role')]['Variable Name'].unique())[0]
        dsg_id['timeseries'] = timeseries_id
        depth_name = list(info_df.loc[(info_df['Row Type'] == 'attribute') & (info_df['Attribute Name'] == 'positive')][
            'Variable Name'].unique())[0]
    return depth_name, dsg_id


def get_time_marks(start, end):
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
    start_obj = datetime.datetime.fromtimestamp(start)
    end_obj = datetime.datetime.fromtimestamp(end)
    label_0 = str(start_obj.strftime('%Y-%m'))
    value_0 = int(start_obj.timestamp())
    label_n = str(end_obj.strftime('%Y-%m'))
    value_n = int(end_obj.timestamp())
    # label = 'mid'
    # value = int((end.timestamp() - start.timestamp())/2)
    # decided not to use the midpoint for the moment
    return {value_0: label_0, value_n: label_n}

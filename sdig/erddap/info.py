import pandas as pd
import datetime
import dateutil.parser
import re
import urllib
import numpy as np


class Info:
    def __init__(self, data_url):
        if data_url.endswith('.html'):
            data_url = re.sub('\\.html$', '', data_url)
        self.url = data_url
        info_url = Info.get_info_url(data_url)
        self.info_df = pd.read_csv(info_url)
        dsg_type_i = list(self.info_df.loc[(self.info_df['Row Type'] == 'attribute') & (self.info_df['Variable Name'] == 'NC_GLOBAL') & (
                self.info_df['Attribute Name'] == 'cdm_data_type')]['Value'].unique())[0]
        self.dsg_type = dsg_type_i.lower()
        
    def get_dsg_type(self):
        """
        Returns the dsg_type of the data set. One of timeseries, profile, trajectory, timeseriesprofile.

        Returns:
            :returns: dsg_type: the dsg type as a lower case string
            :rtype: str
        """
        return self.dsg_type

    def get_dsg_info(self):
        """
        Returns the name of the Z variable as a string and the DSG ID of the data set as a dict
        with keys timeseries, profile, trajectory as appropriate.
        A timeseriesprofile data set has both a timeseries and a profile

        Returns:
            :returns: depth_name: the value of the title global attribute
            :rtype: str
            :returns: dsg_id: the variable names of the id variables as values with [dsg_type] as keys
            :rtype: dict
    
        """
        dsg_id = {}
        depth_name = None
        if self.dsg_type == 'timeseries':
            timeseries_id = list(self.info_df.loc[
                                     (self.info_df['Row Type'] == 'attribute') & (self.info_df['Value'] == 'timeseries_id') & (
                                             self.info_df['Attribute Name'] == 'cf_role')]['Variable Name'].unique())[0]
            dsg_id['timeseries'] = timeseries_id
        elif self.dsg_type == 'trajectory':
            trajectory_id = list(self.info_df.loc[
                                     (self.info_df['Row Type'] == 'attribute') & (self.info_df['Value'] == 'trajectory_id') & (
                                             self.info_df['Attribute Name'] == 'cf_role')]['Variable Name'].unique())[0]
            dsg_id['trajectory'] = trajectory_id
        elif self.dsg_type == 'profile':
            profile_id = list(self.info_df.loc[(self.info_df['Row Type'] == 'attribute') & (self.info_df['Value'] == 'profile_id') & (
                    self.info_df['Attribute Name'] == 'cf_role')]['Variable Name'].unique())[0]
            dsg_id['profile'] = profile_id
    
            # Try to find the vertical proxy first.
            depth_name = None
            depth_series =  self.info_df.loc[
                (self.info_df['Row Type'] == 'attribute') & (self.info_df['Attribute Name'] == 'cdm_altitude_proxy') & (
                        self.info_df['Variable Name'] == 'NC_GLOBAL')]['Value']
            if len(depth_series) > 0:
                depth_name = depth_series.to_list()[0]
    
            if depth_name is None:
                depth_name = list(self.info_df.loc[(self.info_df['Row Type'] == 'attribute') & (self.info_df['Attribute Name'] == 'positive')][
                                      'Variable Name'].unique())[0]
    
        elif self.dsg_type == 'timeseriesprofile':
            profile_id = list(self.info_df.loc[(self.info_df['Row Type'] == 'attribute') & (self.info_df['Value'] == 'profile_id') & (
                    self.info_df['Attribute Name'] == 'cf_role')]['Variable Name'].unique())[0]
            dsg_id['profile'] = profile_id
            timeseries_id = list(self.info_df.loc[
                                     (self.info_df['Row Type'] == 'attribute') & (self.info_df['Value'] == 'timeseries_id') & (
                                             self.info_df['Attribute Name'] == 'cf_role')]['Variable Name'].unique())[0]
            dsg_id['timeseries'] = timeseries_id
            depth_name = None
            att_series = self.info_df.loc[
                (self.info_df['Row Type'] == 'attribute') & (self.info_df['Attribute Name'] == 'cdm_altitude_proxy') & (
                        self.info_df['Variable Name'] == 'NC_GLOBAL')]['Value']
            if len(att_series) > 0:
                depth_name = att_series.to_list()[0]
            if depth_name is None:
                depth_name = list(self.info_df.loc[(self.info_df['Row Type'] == 'attribute') & (self.info_df['Attribute Name'] == 'positive')][
                                      'Variable Name'].unique())[0]
        elif self.dsg_type == 'trajectoryprofile':
            profile_id = list(self.info_df.loc[(self.info_df['Row Type'] == 'attribute') & (self.info_df['Value'] == 'profile_id') & (
                    self.info_df['Attribute Name'] == 'cf_role')]['Variable Name'].unique())[0]
            dsg_id['profile'] = profile_id
            trajectory_id = list(self.info_df.loc[
                                     (self.info_df['Row Type'] == 'attribute') & (self.info_df['Value'] == 'trajectory_id') & (
                                             self.info_df['Attribute Name'] == 'cf_role')]['Variable Name'].unique())[0]
            dsg_id['trajectory'] = trajectory_id
            depth_name = None
            att_series = self.info_df.loc[
                (self.info_df['Row Type'] == 'attribute') & (self.info_df['Attribute Name'] == 'cdm_altitude_proxy') & (
                        self.info_df['Variable Name'] == 'NC_GLOBAL')]['Value']
            if len(att_series) > 0:
                depth_name = att_series.to_list()[0]
            if depth_name is None:
                depth_name = list(self.info_df.loc[(self.info_df['Row Type'] == 'attribute') & (self.info_df['Attribute Name'] == 'positive')][
                                      'Variable Name'].unique())[0]
        return depth_name, dsg_id    

    def get_depths(self):
        """
        Returns a list of depths read directly from an ERDDAP data source.

            Returns:
                    :returns: depths: a sorted list of distinct depths.
                    :rtype: list
        """
        dsg_type = self.get_dsg_type()
        depth_name, dsg_id = self.get_dsg_info()
        depth_url = self.url + '.csv?' + depth_name + '&distinct()&orderBy("' + depth_name + '")'
        depth_df = pd.read_csv(depth_url, skiprows=[1])
        depths = depth_df[depth_name].to_list()
        return depths

    
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
        chk_start_date = self.info_df.loc[
            (self.info_df['Row Type'] == 'attribute') & (self.info_df['Attribute Name'] == 'time_coverage_start') & (
                    self.info_df['Variable Name'] == 'NC_GLOBAL')]['Value'].to_list()[0]
    
        chk_end_date = self.info_df.loc[
            (self.info_df['Row Type'] == 'attribute') & (self.info_df['Attribute Name'] == 'time_coverage_end') & (
                    self.info_df['Variable Name'] == 'NC_GLOBAL')]['Value'].to_list()[0]
    
        start_date_datetime = dateutil.parser.isoparse(chk_start_date)
        end_date_datetime = dateutil.parser.isoparse(chk_end_date)
    
        start_date = start_date_datetime.date().strftime('%Y-%m-%d')
        end_date = end_date_datetime.date().strftime('%Y-%m-%d')
    
        start_date_seconds = start_date_datetime.timestamp()
        end_date_seconds = end_date_datetime.timestamp()
        return start_date, end_date, start_date_seconds, end_date_seconds

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
        variables = list(self.info_df.loc[(self.info_df['Row Type'] == 'attribute') & (self.info_df['Variable Name'] != 'NC_GLOBAL')][
            'Variable Name'].unique())
        long_df_all = self.info_df.loc[(self.info_df['Row Type'] == 'attribute') & (self.info_df['Attribute Name'] == 'long_name')]
        long_df = long_df_all.drop_duplicates(subset=['Variable Name'])
        long_names = dict(zip(long_df['Variable Name'], long_df['Value'].str.capitalize()))
        unit_df = self.info_df.loc[(self.info_df['Row Type'] == 'attribute') & (self.info_df['Attribute Name'] == 'units')]
        units = dict(zip(unit_df['Variable Name'], unit_df['Value']))
        std_nme_all = self.info_df.loc[(self.info_df['Row Type'] == 'attribute') & (self.info_df['Attribute Name'] == 'standard_name')]
        std_nme_df = std_nme_all.drop_duplicates(subset=['Variable Name'])
        standard_names = dict(zip(std_nme_df['Variable Name'], std_nme_df['Value'].astype(str)))
        v_types = list(self.info_df.loc[(self.info_df['Row Type'] == 'variable') & (self.info_df['Variable Name'] != 'NC_GLOBAL')][
                           'Data Type'])
        variable_types = dict(zip(variables, v_types))
        return variables, long_names, units, standard_names, variable_types

    def get_title(self):
        """
        Returns the value of the title global attribute of the data set.

        Returns:
            :returns: title: the value of the title global attribute
            :rtype: str
    
        """
        title = list(self.info_df.loc[(self.info_df['Row Type'] == 'attribute') & (self.info_df['Variable Name'] == 'NC_GLOBAL') & (
                    self.info_df['Attribute Name'] == 'title')]['Value'].unique())[0]
        return title


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
        con = ''
        p_list = []
        if in_platforms is not None:
            if isinstance(in_platforms, list):
                in_platforms = [str(p) for p in in_platforms]
                p_list = in_platforms
                if len(in_platforms) > 1:
                    con = dsg_id_var + '=~"' + urllib.parse.quote('|'.join(in_platforms)) + '"'
                elif len(in_platforms) == 1:
                    con = dsg_id_var + '="' + urllib.parse.quote(in_platforms[0]) + '"'
            else:
                con = dsg_id_var + '="' + urllib.parse.quote(str(in_platforms)) + '"'
                p_list = [str(in_platforms)]
        return {'con': con, 'platforms': p_list}

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
        if data_url.endswith('/index.csv'):
            return data_url
        if data_url.endswith('.html'):
            data_url = re.sub('\\.html$', '', data_url)
        if 'tabledap' in data_url:
            data_url = data_url.replace('tabledap', "info")
        if 'griddap' in data_url:
            data_url = data_url.replace('griddap', "info")
        data_url = data_url + '/index.csv'
        return data_url

    @classmethod
    def plug_gaps(cls, df, time_name, id_name, keep, n_std):
        """
        Inserts a NaN value in every column that is not in the keep list

        :param: df: a Dataframe in which to insert NaN's in time gaps.
        :type: Dataframe
        :param: time_name: the name of the column in the Dataframe that contains the time
        :type: str
        :param: id_name: the column name of the timeseries ID
        :type: str
        :param: list: the names of the columns which are to be copied into the NaN rows
        :type: list
        :param: n_std: the number of standard deviations wide the gap must be to be considered a gap
        :return: The Dataframe with the NaN row in gap
        :rtype: Dataframe
        """
        df[time_name] = pd.to_datetime(df[time_name])
        processed = []
        id_values = df[id_name].unique()
        for e_id in id_values:
            id_df = df[df[id_name]==e_id].copy()
            gaps = id_df['time'].diff()[1:]
            stats = gaps.describe()
            factor = stats['std']*n_std
            if factor > stats['mean']:
                breaks = gaps[gaps>factor]
                after = breaks.index
                before = breaks.index - 1
                insert = breaks.index - .5
                for g in range(0, len(after)):
                    b = before[g]
                    b_row = df.loc[b]
                    i = insert[g]
                    a = after[g]
                    a_row = id_df.loc[a]
                    row = []
                    for col in df.columns:
                        if col == time_name:
                            i_time = b_row[time_name] + (a_row[time_name] - b_row[time_name])/2.0
                            row.append(i_time)
                        elif col in keep:
                            row.append(a_row[col])
                        else:
                            row.append(np.nan)
                    id_df.loc[i] = row
                id_df.sort_index(inplace=True)
                id_df.reset_index(inplace=True, drop=True)
            processed.append(id_df)
        df = pd.concat(processed)
        df = df.reset_index(drop=True)
        return df


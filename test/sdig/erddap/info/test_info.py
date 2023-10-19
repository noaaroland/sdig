import unittest

from sdig.erddap.info import Info
import pandas as pd
import math


class TestEREDDAPInfoMethods(unittest.TestCase):

    def setUp(self):
        self.data_url = 'https://data.pmel.noaa.gov/pmel/erddap/tabledap/CGBN_Canada'
        self.info = Info(self.data_url)

    def test_html_end(self):
        data_url = 'https://data.pmel.noaa.gov/pmel/erddap/tabledap/CGBN_Canada.html'
        info_url = Info.get_info_url(data_url)
        self.assertEqual(info_url, 'https://data.pmel.noaa.gov/pmel/erddap/info/CGBN_Canada/index.csv')

    def test_bare_data(self):
        data_url = 'https://data.pmel.noaa.gov/pmel/erddap/tabledap/CGBN_Canada'
        b_info_url = Info.get_info_url(data_url)
        self.assertEqual(b_info_url, 'https://data.pmel.noaa.gov/pmel/erddap/info/CGBN_Canada/index.csv')

    def test_variables(self):
        variables, long_names, units, standard_names = self.info.get_variables()
        self.assertIn('ID', variables)
        self.assertIn('TAU', variables)
        self.assertEqual(long_names['ID'], 'Ship id')
        self.assertEqual(units['QS'], 'W/m2')
        self.assertEqual(standard_names['latitude'], 'latitude')

    def test_dsg_type(self):
        self.assertEqual('timeseries', self.info.get_dsg_type())

    def test_get_title(self):
        self.assertEqual('CGBN Canadian Arctic Flux 1993-1999', self.info.get_title())

    def test_dsg_info(self):
        depth_name, dsg_id = self.info.get_dsg_info()
        self.assertEqual(depth_name, None)
        self.assertEqual(dsg_id['timeseries'], 'ID')

    def test_times(self):
        start_date, end_date, start_date_seconds, end_date_seconds = self.info.get_times()
        self.assertEqual(start_date, '1993-08-19')
        self.assertEqual(end_date, '1999-11-05')
        self.assertAlmostEqual(start_date_seconds, 745772400.0)
        self.assertAlmostEqual(end_date_seconds, 941824800.0)
        marks = Info.get_time_marks(start_date_seconds, end_date_seconds)
        self.assertEqual(marks[745772400], '1993-08')

    def test_depths(self):
        p_data_url = 'https://data.pmel.noaa.gov/pmel/erddap/tabledap/dy1104_profile_data'
        p_info = Info(p_data_url)
        dsg_type = p_info.get_dsg_type()
        self.assertEqual(dsg_type, 'profile')
        depth_name, dsg_id = p_info.get_dsg_info()
        self.assertEqual(depth_name, 'depth')
        p_id = dsg_id['profile']
        self.assertEqual(p_id, 'id')
        depths = p_info.get_depths()
        # It's just a coincidence that these depths have increments of 1.0
        self.assertAlmostEqual(depths[61], 61.)

    #  Not a public data set...
    # def test_depth_proxy(self):
    #     a_url = 'https://dunkel.pmel.noaa.gov:8930/erddap/tabledap/keo_temp_on_pres.html'
    #     i_url = info.get_info_url(a_url)
    #     a_info_df = pd.read_csv(i_url)
    #     dsg_type = info.get_dsg_type(a_info_df)
    #     depth_name, dsg_id = info.get_dsg_info(dsg_type, a_info_df)
    #     self.assertEqual(depth_name, 'PRES')
    #     depths = info.get_depths(depth_name, a_url)
    #     self.assertGreaterEqual(depths[2], 2.6)

    def test_make_id_con(self):
        platform = '1022.0'
        platforms = ['1040.0', '1041.0', '1095.0']
        r1 = Info.make_platform_constraint('trajectory_id', platform)
        r2 = Info.make_platform_constraint('trajectory_id', platforms)
        self.assertEqual(r1['con'], 'trajectory_id="1022.0"')
        self.assertEqual(type(r1['platforms']), list)
        self.assertEqual(r1['platforms'][0], '1022.0')
        self.assertEqual(r2['con'], 'trajectory_id=~"1040.0|1041.0|1095.0"')

    def test_altitude_proxy(self):
        my_info = Info('https://data.pmel.noaa.gov/alamo/erddap/tabledap/arctic_heat_alamo_profiles_11012')
        dsg_type = my_info.get_dsg_type()
        depth_name, id_d = my_info.get_dsg_info()
        self.assertEqual(dsg_type, 'profile')
        self.assertEqual(id_d[dsg_type], 'profileid')
        self.assertEqual(depth_name, 'PRES')

    def test_trajectoryprofile_id(self):
        tj_info = Info('https://data.pmel.noaa.gov/alamo/erddap/tabledap/arctic_heat_alamo_collection')
        tj_dsg_type = tj_info.get_dsg_type()
        tj_dn, tj_id = tj_info.get_dsg_info()
        self.assertEqual(tj_dsg_type, 'trajectoryprofile')
        self.assertEqual(tj_dn, 'PRES')
        self.assertEqual(tj_id['profile'], 'profileid')
        self.assertEqual(tj_id['trajectory'], 'FLOAT_SERIAL_NO')

    def test_hi_res(self):
        hr_info = Info('https://datalocal.pmel.noaa.gov/erddap/tabledap/sd1069_2019_1hz.html')
        hr_type = hr_info.get_dsg_type()
        self.assertEqual(hr_type, 'trajectory')

    def test_url_encode(self):
        base = 'https://data.pmel.noaa.gov/socat/erddap/tabledap/socat_v2020_decimated.csv?investigators,latitude,longitude,time,expocode,fCO2_recommended&time>=1957-10-21&time<=2020-01-05'
        con_dict = Info.make_platform_constraint('investigators', 'Alin, S. : Sutton, A. : Feely, R.')
        con_dict2 = Info.make_platform_constraint('investigators', ['Alin, S. : Sutton, A. : Feely, R.'])
        self.assertEqual(con_dict['con'], con_dict2['con'])
        e_url = base + '&' + con_dict['con']
        df = pd.read_csv(e_url, skiprows=[1])
        self.assertEqual(df['investigators'].iloc[0], 'Alin, S. : Sutton, A. : Feely, R.')
        con_dict3 = Info.make_platform_constraint('investigators', ['Alin, S. : Sutton, A. : Feely, R.', 'Bakker, D.'])
        e_url = base + '&' + con_dict3['con']
        df = pd.read_csv(e_url, skiprows=[1])
        print(e_url)
        self.assertEqual(df['investigators'].iloc[-1], 'Bakker, D.')

    def test_var_type(self):
        base = 'https://data.pmel.noaa.gov/socat/erddap/tabledap/socat_v2020_decimated'
        scinfo = Info(base)
        variables, long_names, units, standard_names, variable_types = scinfo.get_variables()
        self.assertEqual(variable_types['investigators'], 'String')

    def test_gaps(self):
        url = 'https://data.pmel.noaa.gov/pmel/erddap/tabledap/pmel_co2_moorings_ca69_976d_4677.csv'
        df = pd.read_csv(url, skiprows=[1])
        df = Info.plug_gaps(df, 'time', 'station_id', ['latitude', 'longitude', 'station_id'], 2)
        pd.set_option('display.max_columns', None)
        nan_row = df.loc[374]
        self.assertTrue(math.isnan(nan_row['SST']))


if __name__ == '__main__':
    unittest.main()




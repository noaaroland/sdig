import pandas as pd
import unittest

import sdig.erddap.info as info


class TestEREDDAPInfoMethods(unittest.TestCase):

    info_df = None

    def setUp(self):
        self.info_df = pd.read_csv('https://data.pmel.noaa.gov/pmel/erddap/info/CGBN_Canada/index.csv')

    def test_html_end(self):
        data_url = 'https://data.pmel.noaa.gov/pmel/erddap/tabledap/CGBN_Canada.html'
        data_url = info.get_info_url(data_url)
        self.assertEqual(data_url, 'https://data.pmel.noaa.gov/pmel/erddap/info/CGBN_Canada/index.csv')

    def test_bare_data(self):
        data_url = 'https://data.pmel.noaa.gov/pmel/erddap/tabledap/CGBN_Canada'
        data_url = info.get_info_url(data_url)
        self.assertEqual(data_url, 'https://data.pmel.noaa.gov/pmel/erddap/info/CGBN_Canada/index.csv')

    def test_variables(self):
        variables, long_names, units, standard_names = info.get_variables(self.info_df)
        self.assertIn('ID', variables)
        self.assertIn('TAU', variables)
        self.assertEqual(long_names['ID'], 'Ship id')
        self.assertEqual(units['QS'], 'W/m2')
        self.assertEqual(standard_names['latitude'], 'latitude')

    def test_dsg_type(self):
        self.assertEqual('timeseries', info.get_dsg_type(self.info_df))

    def test_get_title(self):
        self.assertEqual('CGBN Canadian Arctic Flux 1993-1999', info.get_title(self.info_df))

    def test_dsg_info(self):
        depth_name, dsg_id = info.get_dsg_info(info.get_dsg_type(self.info_df), self.info_df)
        self.assertEqual(depth_name, None)
        self.assertEqual(dsg_id['timeseries'], 'ID')

    def test_times(self):
        start_date, end_date, start_date_seconds, end_date_seconds = info.get_times(self.info_df)
        self.assertEqual(start_date, '1993-08-19')
        self.assertEqual(end_date, '1999-11-05')
        self.assertAlmostEqual(start_date_seconds, 745772400.0)
        self.assertAlmostEqual(end_date_seconds, 941824800.0)
        marks = info.get_time_marks(start_date_seconds, end_date_seconds)
        self.assertEqual(marks[745772400], '1993-08')

    def test_depths(self):
        p_data_url = 'https://data.pmel.noaa.gov/pmel/erddap/tabledap/dy1104_profile_data'
        p_info_df = pd.read_csv(info.get_info_url(p_data_url))
        dsg_type = info.get_dsg_type(p_info_df)
        self.assertEqual(dsg_type, 'profile')
        depth_name, dsg_id = info.get_dsg_info(dsg_type, p_info_df)
        self.assertEqual(depth_name, 'depth')
        p_id = dsg_id['profile']
        self.assertEqual(p_id, 'id')
        depths = info.get_depths(depth_name, p_data_url)
        # It's just a coincidence that these depths have increments of 1.0
        self.assertAlmostEqual(depths[61], 61.)

    # Not a public data set...
    # def test_depth_proxy(self):
    #     a_url = 'https://dunkel.pmel.noaa.gov:8930/erddap/tabledap/keo_temp_on_pres.html'
    #     i_url = info.get_info_url(a_url)
    #     a_info_df = pd.read_csv(i_url)
    #     dsg_type = info.get_dsg_type(a_info_df)
    #     depth_name, dsg_id = info.get_dsg_info(dsg_type, a_info_df)
    #     self.assertEqual(depth_name, 'PRES')

    def test_make_id_con(self):
        platform = '1022.0'
        platforms = ['1040.0', '1041.0', '1095.0']
        r1 = info.make_platform_constraint('trajectory_id', platform)
        r2 = info.make_platform_constraint('trajectory_id', platforms)
        self.assertEqual(r1['con'], 'trajectory_id="1022.0"')
        self.assertEqual(type(r1['platforms']), list)
        self.assertEqual(r1['platforms'][0], '1022.0')
        self.assertEqual(r2['con'], 'trajectory_id=~"1040.0|1041.0|1095.0"')


if __name__ == '__main__':
    unittest.main()




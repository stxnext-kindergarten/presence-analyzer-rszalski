# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest

from presence_analyzer import main, views, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)

TEST_USERS_XML = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_users.xml'
)


# pylint: disable=E1103
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config['DATA_CSV'] = TEST_DATA_CSV
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 6)
        self.assertDictEqual(
            data[0],
            {
                u'user_id': 141,
                u'name': u'User 141',
                u'avatar': u'/api/images/users/141',
            },
        )

    def test_mean_time_weekday(self):
        """
        Test mean time weekday.

        Given an existing user_id, it should return mean presence values
        for each weekday in JSON format.
        """
        resp = self.client.get('api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        self.assertListEqual(
            data[1:3],
            [
                [u'Tue', 30047.0],
                [u'Wed', 24465.0],
            ],
        )

    def test_mean_time_weekday_bad_uid(self):
        """
        Test mean time weekday when user does not exist.

        Given a non-existing user_id, it should return an empty list.
        """
        resp = self.client.get('api/v1/mean_time_weekday/999')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 0)
        self.assertListEqual(data, [])

    def test_presence_weekday(self):
        """
        Test presence weekday.

        Given an existing user_id, it should return total presence values
        for each weekday in JSON format.
        """
        resp = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 8)
        self.assertListEqual(
            data[1:3],
            [
                [u'Mon', 0],
                [u'Tue', 30047.0],
            ],
        )

    def test_presence_weekday_bad_uid(self):
        """
        Test presence weekday when user does not exist.

        Given a non-existing user_id, it should return an empty list.
        """
        resp = self.client.get('api/v1/presence_weekday/999')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 0)
        self.assertListEqual(data, [])

    def test_api_presence_start_end(self):
        """
        Test presence weekday start end API.

        Given an existing user_id, it should return JSON data with mean
        Start and End presence values.
        """
        resp = self.client.get('api/v1/presence_start_end/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        self.assertListEqual(
            data,
            [
                [u'Mon', 0, 0],
                [u'Tue', 34745.0, 64792.0],
                [u'Wed', 33592.0, 58057.0],
                [u'Thu', 38926.0, 62631.0],
                [u'Fri', 0, 0],
                [u'Sat', 0, 0],
                [u'Sun', 0, 0],
            ],
        )

    def test_api_presence_start_end_uid(self):
        """
        Test presence weekday start end API when user does not exist.

        Given a non-existing user_id, it should return an empty list.
        """
        resp = self.client.get('api/v1/presence_start_end/999')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 0)
        self.assertListEqual(data, [])

    def test_choose_template_404_view(self):
        """
        Test choose_template view with a non-existing template.

        Choose_template view should return 404 Not Found for a
        non existing template.
        """
        resp = self.client.get('/choose_template/non-existing-template.html')
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.content_type, 'text/html')


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config['DATA_CSV'] = TEST_DATA_CSV
        main.app.config['USERS_XML'] = TEST_USERS_XML

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(data[10][sample_date]['start'],
                         datetime.time(9, 39, 5))

    def test_parse_users_xml(self):
        """
        Test parsing of users XML file.
        """
        data = utils.parse_users_xml()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 6)
        self.assertEqual(
            data[5],
            {
                'user_id': 19,
                'name': 'User 19',
                'avatar': '/api/images/users/141',
            },
        )

    def test_get_server_addr_xml(self):
        """
        Test parsing of server path.
        """
        data = utils.get_server_addr_xml()
        self.assertIsInstance(data, dict)
        self.assertEqual(len(data), 3)
        self.assertDictEqual(
            data,
            {
                'host': 'intranet.stxnext.pl',
                'protocol': 'https',
                'avatar_path': '/api/images/users/',
            }
        )


def suite():
    """
    Default test suite.
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return suite


if __name__ == '__main__':
    unittest.main()

import unittest
import json
from server import create_app, DatabaseManager
import os


class APITestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()
        if os.path.exists('data.sql'):
            os.remove('data.sql')

    def test_create_table(self):
        response = self.client.post('/create_table',
                                    data=json.dumps({
                                        'table_name': 'test_table',
                                        'table_columns_names': ['id', 'name'],
                                        'table_columns_types': ['INTEGER', 'TEXT']
                                    }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Table created:)', response.data)

        # Verify table creation in database
        db_manager = DatabaseManager('data.sql')
        tables = db_manager.fetch_all("sqlite_master")
        table_names = [row['name'] for row in tables if row['type'] == 'table']
        self.assertIn('test_table', table_names)

    def test_write_query(self):
        self.client.post('/create_table',
                         data=json.dumps({
                             'table_name': 'test_table',
                             'table_columns_names': ['id', 'name'],
                             'table_columns_types': ['INTEGER', 'TEXT']
                         }),
                         content_type='application/json')

        response = self.client.post('/write_query',
                                    data=json.dumps({
                                        'table_name': 'test_table',
                                        'table_columns_names': ['id', 'name'],
                                        'values': [1, 'test_name']
                                    }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Data inserted', response.data)

        db_manager = DatabaseManager('data.sql')
        rows = db_manager.fetch_all('test_table')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['id'], 1)
        self.assertEqual(rows[0]['name'], 'test_name')

    def test_create_table_invalid_sql(self):
        response = self.client.post('/create_table',
                                    data=json.dumps({
                                        'table_name': 'test_table_invalid',
                                        'table_columns_names': ['id', 'name'],
                                        'columns_types': ['INTEGER', 'TEXT'] # invalid field name
                                    }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'error', response.data)

    def test_write_query_invalid_values(self):
        self.client.post('/create_table',
                         data=json.dumps({
                             'table_name': 'test_table',
                             'table_columns_names': ['id', 'name'],
                             'table_columns_types': ['INTEGER', 'TEXT']
                         }),
                         content_type='application/json')

        response = self.client.post('/write_query',
                                    data=json.dumps({
                                        'table_name': 'test_table',
                                        'table_columns_names': ['id'],
                                        'values': [1, 'extra_value']  # Extra value
                                    }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'error', response.data)


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
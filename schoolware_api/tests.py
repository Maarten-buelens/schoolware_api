import json
import unittest
from schoolware_api import schoolware

config = json.loads(open("./../schoolware_api_ui/config.json","r").read())

Schoolware = schoolware(config)


class TestSchoolware(unittest.TestCase):
    def test_get_new_token(self):
        result = Schoolware.get_new_token()
        token_length = 36
        self.assertEqual(len(result),token_length)

    def test_get_new_token_schoolware(self):
        result = Schoolware.get_new_token_schoolware()
        token_length = 36
        self.assertEqual(len(result),token_length)

    def test_todo(self):
        result = Schoolware.todo()
        self.assertTrue(isinstance(result, list),"todo not a list")

    def test_punten(self):
        result = Schoolware.punten()
        self.assertTrue(isinstance(result, list),"punten not a list")

    def test_agenda(self):
        result = Schoolware.agenda()
        self.assertTrue(isinstance(result, list),"agenda not a list")

    def test_agenda_week(self):
        result = Schoolware.agenda_week()
        self.assertTrue(isinstance(result, list),"agenda_week not a list")

if __name__ == '__main__':
    unittest.main()
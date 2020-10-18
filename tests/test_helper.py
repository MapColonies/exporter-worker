import unittest
from src.helper import Helper
import json

valid_mock_task = {
    "taskId": "test_taskId",
    "fileName": "test_file_1",
    "directoryName": "test_directory",
    "bbox": [-122.456598, 37.735764, -122.455048, 37.737011],
    "url": "http://10.28.11.95:8600/geoserver/wms?service=WMS&version=1.1.0&request=GetMap&layers=GS_Workspace:i3SF15-meter",
}

invalid_mock_task = {
    "invalid_fields": "test_invalid_fields"
}


class TestHelper(unittest.TestCase):
    def test_valid_json_load(self):
        valid_parsed_task = json.dumps(valid_mock_task)
        result = Helper().load_json(valid_parsed_task)
        self.assertEqual(dict, type(result))

    def test_valid_json_fields_validate(self):
        result = Helper().json_fields_validate(valid_mock_task)
        self.assertEqual(None, result)

    def test_invalid_json_fields_validate(self):
        with self.assertRaises(Exception):
            Helper().json_fields_validate(invalid_mock_task)


if __name__ == '__main__':
    unittest.main()

import unittest
from src.exportImage import is_valid_zoom_for_area


# Zoom level 15
valid_export = {
    "resolution": 2.14576721191406e-05,
    "bbox": [-122.456598, 37.735764, -122.455048, 37.737011]
}

valid_negative_values = {
    "resolution": 2.14576721191406e-05,
    "bbox": [-122.456598, -37.737011, -122.455048, -37.735764]
}

# Zoom level 4
invalid_export = {
    "resolution": 0.0439453125,
    "bbox": [
        35.34901384644131,
        33.0377182656489,
        35.34915987312472,
        33.037930668097495
    ]
}


class TestExport(unittest.TestCase):
    def test_valid_export(self):
        resolution = valid_export["resolution"]
        bbox = valid_export["bbox"]
        result = is_valid_zoom_for_area(resolution, bbox)
        self.assertEqual(result, True)

    def test_valid_negative_export(self):
        resolution = valid_negative_values["resolution"]
        bbox = valid_negative_values["bbox"]
        result = is_valid_zoom_for_area(resolution, bbox)
        self.assertEqual(result, True)

    def test_invalid_export(self):
        resolution = invalid_export["resolution"]
        bbox = invalid_export["bbox"]
        result = is_valid_zoom_for_area(resolution, bbox)
        self.assertEqual(result, False)


if __name__ == '__main__':
    unittest.main()

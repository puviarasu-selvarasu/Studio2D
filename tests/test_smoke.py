import unittest

import studio2d


class Studio2DSmokeTest(unittest.TestCase):
    def test_package_has_version(self):
        self.assertEqual(studio2d.__version__, "0.0.1")


if __name__ == "__main__":
    unittest.main()

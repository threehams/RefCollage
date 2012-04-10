import unittest
from rename_tests_model import TestModelFiles, TestModelNoFiles
from rename_tests_presenter import TestPresenterFiles, TestPresenterNoFiles

if __name__ == "__main__":
    suite = [
        unittest.makeSuite(TestModelFiles),
        unittest.makeSuite(TestModelNoFiles),
        unittest.makeSuite(TestPresenterFiles),
        unittest.makeSuite(TestPresenterNoFiles)]
    alltests = unittest.TestSuite(suite)
    unittest.main()
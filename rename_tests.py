import unittest
from test.rename_tests_model import TestRequiringTemporaryFiles, TestNotRequiringTemporaryFiles
from test.rename_tests_presenter import TestPresenterRequiringTemporaryFiles, TestPresenterNotRequiringTemporaryFiles

if __name__ == "__main__":
    suite = [
        unittest.makeSuite(TestRequiringTemporaryFiles),
        unittest.makeSuite(TestNotRequiringTemporaryFiles),
        unittest.makeSuite(TestPresenterRequiringTemporaryFiles),
        unittest.makeSuite(TestPresenterNotRequiringTemporaryFiles)]
    alltests = unittest.TestSuite(suite)

    runner = unittest.TextTestRunner()
    runner.run(alltests)
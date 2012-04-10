"""
Name        rename_tests_presenter.py
Author      David Edmondson

Tests Presenter interaction with Model, using mock objects for Interactor
and View. Uses images created in a platform-independent temporary directory.
"""
import unittest, os, tempfile
from rename_model import Model
from rename_presenter import Presenter
from rename_tests_objects import Interactor, View

class TestPresenterFiles(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.view = View()
        self.interactor = Interactor()
        self.presenter = Presenter(self.model, self.interactor, self.view)

        self.maxDiff = None

        self.tempImages = [
            "_104!.JPG",
            "31;42;87.jpg",
            "31   .PNG",
            "dash-separated.TIFF",
            "too.many.dots.png.jpg",
            "32165342_a7d7351d30_o.jpg",
            "6795654383_a7d7351d30_z.jpg",
            "6888049103_0e43f63926_o.jpg",
            "679563_a30_z.exe",
            "init.ini"]

        self.root = tempfile.mkdtemp()
        for fn in self.tempImages:
            open(os.path.join(self.root, fn), "w+b").close()

    def tearDown(self):
        for fn in self.tempImages:
            os.remove(os.path.join(self.root, fn))

    def testOpenPath(self):
        expected = {
            "_104!.JPG":"104!.jpg",
            "31   .PNG":"31.png",
            "dash-separated.TIFF":"dash separated.tiff",
            "too.many.dots.png.jpg":"too many dots png.jpg",
            "32165342_a7d7351d30_o.jpg":"32165342 a7d7351d30 o.jpg",
            "6795654383_a7d7351d30_z.jpg":"6795654383 a7d7351d30 z.jpg",
            "6888049103_0e43f63926_o.jpg":"6888049103 0e43f63926 o.jpg"}
        old, new = [], []
        expectedKeys = sorted(expected.keys(),
                              key=lambda k: (k.rsplit(os.sep)[0], k.lower()),
                              reverse=True)
        for key in expectedKeys:
            old.append(key)
            new.append(expected[key])
        settings = {
            "delimiter":" ",
            "flickr":False,
            "capital":False}
        self.model.changeSettings(settings)
        self.model._lastPath = self.root
        self.presenter.openPath()

        oldFn, newFn = self.view.rename
        for k, v in zip(old, new):
            self.assertIn(k, oldFn)
            self.assertIn(v, newFn)

class TestPresenterNoFiles(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.view = View()
        self.interactor = Interactor()
        self.presenter = Presenter(self.model, self.interactor, self.view)

        self.maxDiff = None

    def testSettingsChanged(self):
        self.view.flickr = True
        self.view.capital = True
        self.view.delimiter = "-"
        self.presenter.settingsChanged()
        self.assertEqual(self.model._flickr, True)
        self.assertEqual(self.model._capital, True)
        self.assertEqual(self.model._delimiter, "-")

        self.view.flickr = False
        self.view.capital = False
        self.view.delimiter = " "
        self.presenter.settingsChanged()
        self.assertEqual(self.model._flickr, False)
        self.assertEqual(self.model._capital, False)
        self.assertEqual(self.model._delimiter, " ")

    def testSetOptions(self):
        self.model._lastPath = ""
        self.view.capital = True
        self.view.flickr = True
        self.view.delimiter = '_'
        expectSettings = {"capital":True,
                          "flickr":True,
                          "delimiter":"_",
                          "lastPath":""}
        self.presenter.settingsChanged()
        self.assertDictEqual(self.model.getSettings(), expectSettings)

        self.view.capital = False
        self.view.flickr = False
        self.view.delimiter = ' '
        expectSettings = {"capital":False,
                          "flickr":False,
                          "delimiter":" ",
                          "lastPath":""}
        self.presenter.settingsChanged()
        self.assertDictEqual(self.model.getSettings(), expectSettings)

if __name__ == '__main__':
    unittest.main()
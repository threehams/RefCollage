import unittest, os, tempfile
from rename_model import Model
from rename_presenter import Presenter
from rename_tests_objects import Interactor, View

class TestsPresenter(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.view = View()
        self.interactor = Interactor()
        self.presenter = Presenter(self.model, self.interactor, self.view)

        self.maxDiff = None

    def _createTempFiles(self):
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
            "init.ini"
        ]

        root = tempfile.mkdtemp()
        for fn in self.tempImages:
            open(os.path.join(root, fn), "w+b").close()
        return root

    def _removeTempFiles(self, root):
        for fn in self.tempImages:
            os.remove(os.path.join(root, fn))

    def testOpenPath(self):
        root = self._createTempFiles()
        expected = {
            "_104!.JPG":"104!.jpg",
            "31   .PNG":"31.png",
            "dash-separated.TIFF":"dash separated.tiff",
            "too.many.dots.png.jpg":"too many dots png.jpg",
            "32165342_a7d7351d30_o.jpg":"32165342 a7d7351d30 o.jpg",
            "6795654383_a7d7351d30_z.jpg":"6795654383 a7d7351d30 z.jpg",
            "6888049103_0e43f63926_o.jpg":"6888049103 0e43f63926 o.jpg"
        }
        expected = {
            os.path.join(root, k) : os.path.join(root, v)
            for (k, v) in expected.items()
        }
        settings = {
            "delimiter":" ",
            "flickr":False,
            "capital":False
        }
        self.model.changeSettings(settings)
        self.model._lastPath = root
        self.presenter.openPath()
        self.assertDictEqual(expected, self.view.rename)

        self._removeTempFiles()

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
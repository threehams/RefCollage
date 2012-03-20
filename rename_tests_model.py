"""
Name        rename_tests_model.py
Author      David Edmondson

Tests Model-specific methods for basic functionality. Uses images created in
a platform-independent temporary directory.
"""

import unittest, os, tempfile, json
from rename_model import Model

class MyTestCase(unittest.TestCase):
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

    def testGetRenameList(self):
        """Test that the correct files are found and renamed."""
        self.maxDiff = None

        root = self._createTempFiles()
        testSpaceFlickr = {
            "_104!.JPG":                   "104!.jpg",
            "31   .PNG":                   "31.png",
            "dash-separated.TIFF":         "dash separated.tiff",
            "too.many.dots.png.jpg":       "too many dots png.jpg",
            "32165342_a7d7351d30_o.jpg":   "32165342 a7d7351d30 o.jpg",
            "6795654383_a7d7351d30_z.jpg": "And loves the noblest frailty of the mind John Dryden.jpg",
            "6888049103_0e43f63926_o.jpg": "DughiTile Oakwd KARL.jpg"
        }
        testSpaceFlickr = {
            os.path.join(root, k) : os.path.join(root, v)
            for (k, v) in testSpaceFlickr.items()
        }
        testUnderscoreCapitalFlickr = {
            "_104!.JPG":                   "104!.jpg",
            "31   .PNG":                   "31.png",
            "dash-separated.TIFF":         "Dash_Separated.tiff",
            "too.many.dots.png.jpg":       "Too_Many_Dots_Png.jpg",
            "32165342_a7d7351d30_o.jpg":   "32165342_A7D7351D30_O.jpg",
            "6795654383_a7d7351d30_z.jpg": "And_Loves_The_Noblest_Frailty_Of_The_Mind_John_Dryden.jpg",
            "6888049103_0e43f63926_o.jpg": "Dughitile_Oakwd_Karl.jpg"
        }
        testUnderscoreCapitalFlickr = {
            os.path.join(root, k) : os.path.join(root, v)
            for (k, v) in testUnderscoreCapitalFlickr.items()
        }

        m = Model()
        m._capital = False
        m._flickr = True
        m._delimiter = " "

        m.createRenameList(root)
        resultList = m.getRenameList()
        self.assertDictEqual(testSpaceFlickr, resultList)

        m = Model()
        m._capital = True
        m._flickr = True
        m._delimiter = "_"

        m.createRenameList(root)
        resultList = m.getRenameList()
        self.assertDictEqual(testUnderscoreCapitalFlickr, resultList)

        self._removeTempFiles(root)

    def testGetRedirect(self):
        """Test that the function catches 404 and authentication issues."""
        m = Model()
        m._flickr = True
        m._capital = False
        m._delimiter = " "
        self.assertEqual(
            m._getRedirect("flickr.com", "/photo.gne?id=2816803094"),
            "/photos/30073770@N07/2816803094"
        )
        self.assertIn(
            "signin",
            m._getRedirect("flickr.com", "/photo.gne?id=2816803022")
        )
        self.assertEqual(
            m._getRedirect("flickr.com", "/photo.gne?id=9216803042"),
            None
        )


    def testLoadSettings(self):
        """Test that settings are correctly loaded, and exceptions are raised."""
        m = Model()

        expectSettings = {"flickr":True,
                          "capital":True,
                          "delimiter":" ",
                          "lastPath":""
        }

        f = open(m.FILE_SETTINGS, "w+")
        json.dump(expectSettings, f)
        f.close()

        m._loadSettings()
        settings = m.getSettings()
        self.assertDictEqual(settings, expectSettings)

    def testCheckDuplicates(self):
        """Test that duplicate checking functions."""
        m = Model()
        m._flickr = False
        m._capital = False
        m._delimiter = " "

        m._renameList = {
            "42_24.jpg":"42 24.jpg",
            "42_42.jpg":"42 42.jpg",
            "42-42.jpg":"42 42 (1).jpg",
            "42.jpg.png":"42.jpg.png",
        }
        self.assertEqual(m._checkDuplicates("42 24.jpg"), "42 24 (1).jpg")
        self.assertEqual(m._checkDuplicates("42 42.jpg"), "42 42 (2).jpg")
        self.assertEqual(m._checkDuplicates("42.jpg.png"), "42.jpg (1).png")

    def testIsFlickr(self):
        """Test that images are correctly identified as having Flickr
        naming conventions, and return ID and extension."""

        # Test with Flickr on
        m = Model()
        m._flickr = True

        self.assertEqual(
            m._isFlickr("6795654383_a7d7351d30_z.jpg"), "6795654383")
        self.assertEqual(
            m._isFlickr("4321305_2309f0b_m.jpeg"), "4321305")
        self.assertFalse(
            m._isFlickr("23102211321532_2012B_o.JPG"))
        self.assertFalse(m._isFlickr("32165342_a7d7351d30"))

        # Test with Flickr off
        m._flickr = False
        self.assertFalse(m._isFlickr("23102211_2012f_o.JPG"))

    def testConvertName(self):
        """Tests name conversion with many different options."""
        m = Model()
        m._capital = True
        m._flickr = False
        m._delimiter = " "
        self.assertEqual(m._convertName("an_image__with_underscores.png"),
                    "An Image With Underscores.png")
        self.assertEqual(m._convertName("too    much     space.jpg"),
                    "Too Much Space.jpg")
        m._delimiter = "_"
        self.assertEqual(m._convertName("name with spaces.tif"),
                    "Name_With_Spaces.tif")
        self.assertEqual(m._convertName("TOO    muCH     spAce.tga"),
                    "Too_Much_Space.tga")
        self.assertRaises(TypeError, lambda: m._convertName("blank_name"))
        m._capital = False
        self.assertEqual(m._convertName("ALL CAPS.tif"),
                    "ALL_CAPS.tif")
        self.assertEqual(m._convertName("TOO    muCH     spAce.tga"),
                    "TOO_muCH_spAce.tga")

    def testGetNameFlickr(self):
        """Test that Flickr name retrieval works correctly."""
        m = Model()
        m._capital = True
        m._flickr = True
        m._delimiter = " "
        self.assertEqual(
            m._getNameFlickr("6888049103_201246b2f_m.jpg", "6888049103"),
            "Dughitile Oakwd Karl.jpg")
        self.assertEqual(
            m._getNameFlickr("6795654383_10234fb2_z.jpg", "6795654383"),
            "And Loves The Noblest Frailty Of The Mind John Dryden.jpg")
        self.assertEqual(
            m._getNameFlickr("32165342_a7d7351d30_o.jpeg", "32165342"),
            "32165342 A7D7351D30 O.jpeg")
        self.assertEqual(
            m._getNameFlickr("178933701_77d7b5448f.jpg", "178933701"),
            "Apartment Roof.jpg")

    def testImageCheck(self):
        """Checks that only images are renamed."""
        m = Model()
        listImages = ("image.bmp", "image.png", "a.jpeg", "UPPER.JPG",
            "mixedCase.Tiff", "sp a ces.tif")
        listNotImages = ("not_image", "autoexec.bat", "auto.exe",
            "soundboard.wav", "", " ", "message.php", "..", "complex.gif.bat")
        listTypeError = (["s1", "s2"], None, False)

        for fn in listImages:
            self.assertTrue(m._isImage(fn))
        for fn in listNotImages:
            self.assertFalse(m._isImage(fn))
        for fn in listTypeError:
            self.assertRaises(AttributeError, lambda: m._isImage(fn))

if __name__ == '__main__':
    unittest.main()
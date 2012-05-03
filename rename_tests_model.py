"""
Name        rename_tests_model.py
Author      David Edmondson

Tests Model-specific methods for basic functionality. Uses images created in
a platform-independent temporary directory.
"""

import unittest, os, tempfile, json
from rename_model import Model

class TestRequiringTemporaryFiles(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

        # Instantiate model
        self.m = Model()

        # Create temporary directory and files
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
        os.rmdir(self.root)

    def _changeSettings(self, capital, flickr, delimiter, lastPath=""):
        settings = {"capital": capital,
                    "flickr": flickr,
                    "delimiter": delimiter,
                    "lastPath": lastPath}
        self.m.changeSettings(settings)

    def testRenameList_SpaceFlickr(self):
        """Test that the correct files are found and renamed with space
        delimiter and Flickr name lookup."""
        self._changeSettings(capital=False, flickr=True, delimiter=" ")

        testSpaceFlickr = {
            os.path.join(self.root, "_104!.JPG"):                   os.path.join(self.root, "104!.jpg"),
            os.path.join(self.root, "31   .PNG"):                   os.path.join(self.root, "31.png"),
            os.path.join(self.root, "dash-separated.TIFF"):         os.path.join(self.root, "dash separated.tiff"),
            os.path.join(self.root, "too.many.dots.png.jpg"):       os.path.join(self.root, "too many dots png.jpg"),
            os.path.join(self.root, "32165342_a7d7351d30_o.jpg"):   os.path.join(self.root, "32165342 a7d7351d30 o.jpg"),
            os.path.join(self.root, "6795654383_a7d7351d30_z.jpg"): os.path.join(self.root, "And loves the noblest frailty of the mind John Dryden.jpg"),
            os.path.join(self.root, "6888049103_0e43f63926_o.jpg"): os.path.join(self.root, "DughiTile Oakwd KARL.jpg")}

        self.m.createRenameList(self.root)
        resultList = self.m.getRenameList()
        self.assertDictEqual(testSpaceFlickr, resultList)

    def testRenameList_UnderscoreCapitalFlickr(self):
        """Test that the correct files are found and renamed with underscore
        delimiter, capitalization on, and Flickr name lookup."""
        self._changeSettings(capital=True, flickr=True, delimiter="_")

        testUnderscoreCapitalFlickr = {
            os.path.join(self.root, "_104!.JPG"):                   os.path.join(self.root, "104!.jpg"),
            os.path.join(self.root, "31   .PNG"):                   os.path.join(self.root, "31.png"),
            os.path.join(self.root, "dash-separated.TIFF"):         os.path.join(self.root, "Dash_Separated.tiff"),
            os.path.join(self.root, "too.many.dots.png.jpg"):       os.path.join(self.root, "Too_Many_Dots_Png.jpg"),
            os.path.join(self.root, "32165342_a7d7351d30_o.jpg"):   os.path.join(self.root, "32165342_A7D7351D30_O.jpg"),
            os.path.join(self.root, "6795654383_a7d7351d30_z.jpg"): os.path.join(self.root, "And_Loves_The_Noblest_Frailty_Of_The_Mind_John_Dryden.jpg"),
            os.path.join(self.root, "6888049103_0e43f63926_o.jpg"): os.path.join(self.root, "Dughitile_Oakwd_Karl.jpg")}

        self.m.createRenameList(self.root)
        resultList = self.m.getRenameList()
        self.assertDictEqual(testUnderscoreCapitalFlickr, resultList)

    def testRenameList_DotCapital(self):
        """Test that the correct files are found and renamed with period
        delimiter, capitalization on, and no Flickr name lookup."""
        self._changeSettings(capital=True, flickr=False, delimiter=".")

        testUnderscoreCapitalFlickr = {
            os.path.join(self.root, "_104!.JPG"):                   os.path.join(self.root, "104!.jpg"),
            os.path.join(self.root, "31   .PNG"):                   os.path.join(self.root, "31.png"),
            os.path.join(self.root, "dash-separated.TIFF"):         os.path.join(self.root, "Dash.Separated.tiff"),
            os.path.join(self.root, "too.many.dots.png.jpg"):       os.path.join(self.root, "Too.Many.Dots.Png.jpg"),
            os.path.join(self.root, "32165342_a7d7351d30_o.jpg"):   os.path.join(self.root, "32165342.A7D7351D30.O.jpg"),
            os.path.join(self.root, "6795654383_a7d7351d30_z.jpg"): os.path.join(self.root, "6795654383.A7D7351D30.Z.jpg"),
            os.path.join(self.root, "6888049103_0e43f63926_o.jpg"): os.path.join(self.root, "6888049103.0E43F63926.O.jpg")}

        self.m.createRenameList(self.root)
        resultList = self.m.getRenameList()
        self.assertDictEqual(testUnderscoreCapitalFlickr, resultList)

    def testRunRenameFiles(self):
        pass

class TestNotRequiringTemporaryFiles(unittest.TestCase):
    def setUp(self):
        # Instantiate model, force all settings to default
        self.m = Model()

    def _changeSettings(self, capital, flickr, delimiter, lastPath=""):
        settings = {"capital": capital,
                    "flickr": flickr,
                    "delimiter": delimiter,
                    "lastPath": lastPath}
        self.m.changeSettings(settings)

    def testGetRedirect(self):
        """Test that the function catches 404 and authentication issues."""
        self._changeSettings(capital=False, flickr=True, delimiter=" ")
        self.assertEqual(
            self.m._getRedirect("flickr.com", "/photo.gne?id=2816803094"),
            "/photos/30073770@N07/2816803094")
        self.assertIn(
            "signin",
            self.m._getRedirect("flickr.com", "/photo.gne?id=2816803022"))
        self.assertEqual(
            self.m._getRedirect("flickr.com", "/photo.gne?id=9216803042"),
            None)

    def testLoadSettings(self):
        """Test that settings are correctly loaded."""
        expectSettings = {"flickr":True,
                          "capital":True,
                          "delimiter":" ",
                          "lastPath":""}

        f = open(self.m.FILE_SETTINGS, "w+")
        json.dump(expectSettings, f)
        f.close()

        self.m._loadSettings()
        settings = self.m.getSettings()
        self.assertDictEqual(settings, expectSettings)

    def testNoSettingsFile(self):
        """Test that a settings file is created with correct defaults."""
        os.remove(self.m.FILE_SETTINGS)

        self.m = Model()
        settings = self.m.getSettings()
        self.assertDictEqual(self.m.SETTING_DEFAULT, settings)

    def testInvalidSettingsFile(self):
        """Test that invalid or missing settings on disk are replaced with defaults."""
        invalidSettings = {"capital":"Canberra",
                          "delimiter":";",
                          "lastPath":False}
        expectedSettings = self.m.SETTING_DEFAULT

        f = open(self.m.FILE_SETTINGS, "w+")
        json.dump(invalidSettings, f)
        f.close()

        self.m = Model()
        self.assertDictEqual(self.m.getSettings(), expectedSettings)


    def testCheckDuplicates(self):
        """Test that duplicate checking functions."""
        self._changeSettings(capital=False, flickr=False, delimiter=" ")

        self.m._renameList = {
            "42_24.jpg":"42 24.jpg",
            "42_42.jpg":"42 42.jpg",
            "42-42.jpg":"42 42 (1).jpg",
            "42.jpg.png":"42.jpg.png"}
        self.assertEqual(self.m._checkDuplicates("42 24.jpg"), "42 24 (1).jpg")
        self.assertEqual(self.m._checkDuplicates("42 42.jpg"), "42 42 (2).jpg")
        self.assertEqual(self.m._checkDuplicates("42.jpg.png"), "42.jpg (1).png")
        self.assertEqual(self.m._checkDuplicates("notADuplicate.png"), None)

    def testIsFlickr(self):
        """Test that images are correctly identified as having Flickr
        naming conventions, and return ID and extension."""

        # Test with Flickr on
        self._changeSettings(capital=False, flickr=True, delimiter=" ")

        self.assertEqual(
            self.m._isFlickr("6795654383_a7d7351d30_z.jpg"), "6795654383")
        self.assertEqual(
            self.m._isFlickr("4321305_2309f0b_m.jpeg"), "4321305")
        self.assertFalse(
            self.m._isFlickr("23102211321532_2012B_o.JPG"))
        self.assertFalse(self.m._isFlickr("32165342_a7d7351d30"))

        # Test with Flickr off
        self.m._flickr = False
        self.assertFalse(self.m._isFlickr("23102211_2012f_o.JPG"))

    def testConvertName(self):
        """Tests name conversion with many different options."""
        self._changeSettings(capital=True, flickr=False, delimiter=" ")

        self.assertEqual(self.m._convertName("an_image__with_underscores.png"),
                    "An Image With Underscores.png")
        self.assertEqual(self.m._convertName("too    much     space.jpg"),
                    "Too Much Space.jpg")

        self._changeSettings(capital=True, flickr=False, delimiter="_")
        self.assertEqual(self.m._convertName("name with spaces.tif"),
                    "Name_With_Spaces.tif")
        self.assertEqual(self.m._convertName("TOO    muCH     spAce.tga"),
                    "Too_Much_Space.tga")
        self.assertRaises(TypeError, lambda: self.m._convertName("blank_name"))

        self._changeSettings(capital=False, flickr=False, delimiter="_")
        self.assertEqual(self.m._convertName("ALL CAPS.tif"),
                    "ALL_CAPS.tif")
        self.assertEqual(self.m._convertName("TOO    muCH     spAce.tga"),
                    "TOO_muCH_spAce.tga")

    def testGetNameFlickr(self):
        """Test that Flickr name retrieval works correctly."""
        self._changeSettings(capital=True, flickr=True, delimiter=" ")
        self.assertEqual(
            self.m._getNameFlickr("6888049103_201246b2f_m.jpg", "6888049103"),
            "Dughitile Oakwd Karl.jpg")
        self.assertEqual(
            self.m._getNameFlickr("6795654383_10234fb2_z.jpg", "6795654383"),
            "And Loves The Noblest Frailty Of The Mind John Dryden.jpg")
        self.assertEqual(
            self.m._getNameFlickr("32165342_a7d7351d30_o.jpeg", "32165342"),
            "32165342 A7D7351D30 O.jpeg")
        self.assertEqual(
            self.m._getNameFlickr("178933701_77d7b5448f.jpg", "178933701"),
            "Apartment Roof.jpg")

    def testImageCheck(self):
        """Checks that only images are renamed."""
        listImages = ("image.bmp", "image.png", "a.jpeg", "UPPER.JPG",
            "mixedCase.Tiff", "sp a ces.tif")
        listNotImages = ("not_image", "autoexec.bat", "auto.exe",
            "soundboard.wav", "", " ", "message.php", "..", "complex.gif.bat")
        listTypeError = (["s1", "s2"], None, False)

        for fn in listImages:
            self.assertTrue(self.m._isImage(fn))
        for fn in listNotImages:
            self.assertFalse(self.m._isImage(fn))
        for fn in listTypeError:
            self.assertRaises(AttributeError, lambda: self.m._isImage(fn))

if __name__ == '__main__':
    unittest.main()
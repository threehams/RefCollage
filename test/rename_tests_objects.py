"""
Name        rename_tests_objects.py
Author      David Edmondson

Mock objects for Presenter testing. All UI-specific functionality stripped out,
allowing this to run with no input.
"""

class DialogOpenFolder(object):
    pass

class ListCtrlRename(object):
    pass

class View(object):
    def __init__(self, *args, **kwargs):
        self._comboBoxDelimiter = {
            "selected":'',
            "options":[]}
        self._checkboxFlickr = False
        self._checkboxCapital = False
        self._listRename = [
            [],
            []]

    def start(self):
        pass

    def start(self):
        pass

    def resizeColumns(self, width):
        pass

    def openDir(self, lastPath):
        return lastPath

    def showError(self, title, message):
        pass

    def showInfo(self, title, message):
        pass

    def showConfirm(self, title, message):
        return True

    def showProgress(self, progress, title = "", message = "", abort=False):
        return True

    def stopProgress(self):
        return True

    def showHelpBox(self):
        pass

    def showAboutBox(self):
        pass

    # Properties for getting / setting - necessary for translation to wx
    def enableButtonRename(self, state):
        pass

    # Properties to keep wxPython syntax restricted to the View.
    def _getListRename(self):
        return self._listRename[0], self._listRename[1]

    def _setListRename(self, (list1, list2)):
        self._listRename[0] = list1
        self._listRename[1] = list2

    def _getComboBoxDelimiter(self):
        return self._comboBoxDelimiter["selected"]

    def _setComboBoxDelimiter(self, value):
        self._comboBoxDelimiter["selected"] = value

    def _getDelimiterOptions(self):
        return self._comboBoxDelimiter["options"]

    def _setDelimiterOptions(self, options):
        self._comboBoxDelimiter["options"] = options

    def _getCheckboxFlickr(self):
        return self._checkboxFlickr

    def _setCheckboxFlickr(self, value):
        self._checkboxFlickr = value

    def _getCheckboxCapital(self):
        return self._checkboxCapital

    def _setCheckboxCapital(self, value):
        self._checkboxCapital = value

    rename = property(_getListRename, _setListRename)
    delimiter = property(_getComboBoxDelimiter, _setComboBoxDelimiter)
    delimiterOptions = property(_getDelimiterOptions, _setDelimiterOptions)
    flickr = property(_getCheckboxFlickr, _setCheckboxFlickr)
    capital = property(_getCheckboxCapital, _setCheckboxCapital)

class Interactor(object):
    def install(self, presenter, view):
        pass
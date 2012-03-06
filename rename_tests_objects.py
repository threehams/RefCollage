import wx

class DialogOpenFolder(wx.DirDialog):
    def __init__(self, *args, **kwargs):
        wx.DirDialog.__init__(self, *args, **kwargs)

class ListCtrlRename(wx.ListCtrl):
    def __init__(self, parent=None, style=wx.LC_REPORT|wx.BORDER_SUNKEN,
                 *args, **kwargs):
        wx.ListCtrl.__init__(self, parent=parent, style=style, *args, **kwargs)
        self.InsertColumn(0, 'Old Name')
        self.InsertColumn(1, 'New Name')

class View(wx.Frame):
    def __init__(self, *args, **kwargs):
        self._comboBoxDelimiter = {}
        self._comboBoxDelimiter["selected"] = ''
        self._comboBoxDelimiter["options"] = []
        self._checkboxFlickr = False
        self._checkboxCapital = False
        self._listRename = []

    def start(self):
        pass

    def enableButtonRename(self, state):
        pass

    def resizeColumns(self, width):
        pass

    # Properties to keep wxPython syntax restricted to the View.
    def _getListRename(self):
        return self._listRename

    def _setListRename(self, dict_):
        _listRename = _dict[:]

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

import wx

class Interactor(object):
    def install(self, presenter, view):
        pass
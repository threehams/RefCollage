import wx, os

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
        wx.Frame.__init__(self, *args, **kwargs)

        self.SetTitle("Image Renamer")
        self.SetSize((640,480))

        menuBar = wx.MenuBar()
        menuFile = wx.Menu()
        self.menuFileOpen = menuFile.Append(wx.ID_OPEN, '&Open Folder',
                                       'Select a directory')
        self.menuFileQuit = menuFile.Append(wx.ID_EXIT, '&Quit',
                                            'Quit application')

        menuHelp = wx.Menu()
        self.menuHelpHelp = menuHelp.Append(wx.ID_HELP, '&Help',
                                            'View Help files')
        self.menuHelpAbout = menuHelp.Append(wx.ID_ABOUT, '&About',
                                        'About this program')

        #menuOptions = wx.MenuBar()
        #menuOptions.Append(wx.ID_PREFERENCES, '&Preferences',
        #                'Select program options')

        menuBar.Append(menuFile, title="&File")
        menuBar.Append(menuHelp, title="&Help")

        panel = wx.Panel(self)

        sizer = wx.GridBagSizer(7,3)

        boxDropdowns = wx.BoxSizer(orient=wx.HORIZONTAL)
        textDelimiter = wx.StaticText(panel, label="Delimiter")
        self._comboBoxDelimiter = wx.ComboBox(panel)
        boxDropdowns.Add(textDelimiter, flag=wx.LEFT|wx.TOP, border=5)
        boxDropdowns.Add(self._comboBoxDelimiter, flag=wx.LEFT|wx.TOP, border=5)

        sizer.Add(boxDropdowns, pos=(0,0))

        line = wx.StaticLine(panel)
        sizer.Add(line, pos=(1,0), span=(1,3),
                  flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=10)

        self._checkboxFlickr = wx.CheckBox(panel, label="Flickr Lookup")
        self._checkboxCapital = wx.CheckBox(panel, label="Capital")

        sizer.Add(self._checkboxFlickr, pos=(2,0))
        sizer.Add(self._checkboxCapital, pos=(3,0))

        self._listRename = ListCtrlRename(panel, size=(-1,200))
        sizer.Add(self._listRename, pos=(4,0), span=(1,3), flag=wx.EXPAND)

        self.buttonOpen = wx.Button(panel, label="Select Folder")
        self.buttonRename = wx.Button(panel, label="Rename Files")

        sizer.Add(self.buttonOpen, pos=(5,1))
        sizer.Add(self.buttonRename, pos=(5,2))

        #self.SetMenuBar(menuBar)

        sizer.AddGrowableCol(0)
        sizer.AddGrowableRow(4)

        panel.SetSizer(sizer)

        self.SetMenuBar(menuBar)

        self.Centre()
        self.Show()

    def start(self):
        self.app = wx.App()
        self.app.MainLoop()

    def openDir(self, lastPath):
        dlg = DialogOpenFolder(self, defaultPath = lastPath)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            path = dlg.GetPath()
            self._lastPath = path
            return path
        return None

    def showError(self, errorText):
        dlg = wx.MessageDialog(None, message=errorText, caption="Error",
                               style=wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()

    def showInfo(self, infoTitle, infoText):
        dlg = wx.MessageDialog(None, message=infoText, caption=infoTitle,
                               style=wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def showConfirm(self, confirmTitle, confirmText):
        dlg = wx.MessageDialog(None, caption=confirmTitle, message=confirmText,
                               style=wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            return True
        return False

    # Properties for getting / setting - necessary for translation to wx
    def enableButtonRename(self, state):
        if state:
            self.buttonRename.Enable()
        else:
            self.buttonRename.Disable()

    def _getListRename(self):
        # TODO: Give this a real get method if it's ever needed
        return None

    def _setListRename(self, dict_):
        # TODO: Allow custom sorting
        self._listRename.DeleteAllItems()
        # Sort first by path, then file
        for oldFn in sorted(
                            dict_.keys(),
                            key=lambda k: (k.rsplit(os.sep)[0], k.lower()),
                            reverse=True):
            pos = self._listRename.InsertStringItem(0, oldFn)
            self._listRename.SetStringItem(pos, 1, dict_[oldFn])

    def _getComboBoxDelimiter(self):
        return self._comboBoxDelimiter.GetValue()

    def _setComboBoxDelimiter(self, value):
        self._comboBoxDelimiter.SetValue(value)

    def _getDelimiterOptions(self):
        return self._comboBoxDelimiter.GetItems()

    def _setDelimiterOptions(self, options):
        self._comboBoxDelimiter.Clear()
        self._comboBoxDelimiter.AppendItems(options)

    def _getCheckboxFlickr(self):
        return self._checkboxFlickr.GetValue()

    def _setCheckboxFlickr(self, value):
        self._checkboxFlickr.SetValue(value)

    def _getCheckboxCapital(self):
        return self._checkboxCapital.GetValue()

    def _setCheckboxCapital(self, value):
        self._checkboxCapital.SetValue(value)

    rename = property(_getListRename, _setListRename)
    delimiter = property(_getComboBoxDelimiter, _setComboBoxDelimiter)
    delimiterOptions = property(_getDelimiterOptions, _setDelimiterOptions)
    flickr = property(_getCheckboxFlickr, _setCheckboxFlickr)
    capital = property(_getCheckboxCapital, _setCheckboxCapital)

if __name__ == "__main__":
    app = wx.App()
    view = View(parent=None)
    app.MainLoop()
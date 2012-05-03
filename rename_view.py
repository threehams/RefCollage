"""
Name        rename_view.py
Author      David Edmondson, adapted from sample by Peter Damoc

View is as passive as possible, receiving data updates from the Presenter, and
translating wx-specific dialogs and codes into Pythonic language.

The Presenter should not call any wx-specific methods. The View can currently be
replaced with any other UI toolkit, with changes only made to the Interactor.
"""

import wx

class DialogOpenFolder(wx.DirDialog):
    def __init__(self, *args, **kwargs):
        wx.DirDialog.__init__(self, *args, **kwargs)

class ListCtrlRename(wx.ListCtrl):
    def __init__(self, parent=None, style=wx.LC_REPORT|wx.BORDER_SUNKEN,
                 *args, **kwargs):
        wx.ListCtrl.__init__(self, parent=parent, style=style, *args, **kwargs)
        self.InsertColumn(0, u'Old Name')
        self.InsertColumn(1, u'New Name')

class View(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self._progress = None

        self.SetTitle(u"Image Renamer")
        self.SetSize((800,600))

        panel = wx.Panel(self)

        self._comboBoxDelimiter = wx.ComboBox(panel)
        self._checkboxFlickr = wx.CheckBox(panel, label=u"Flickr Lookup")
        self._checkboxCapital = wx.CheckBox(panel, label=u"Capital")
        self._listRename = ListCtrlRename(panel)
        self.buttonOpen = wx.Button(panel, label=u"Select Folder")
        self.buttonRename = wx.Button(panel, label=u"Rename Files")
        self._textPath = wx.TextCtrl(panel)

        # Menus first
        menuBar = wx.MenuBar()
        menuFile = wx.Menu()
        self.menuFileOpen = menuFile.Append(wx.ID_OPEN, u'&Open Folder\tCtrl+O',
                                       u'Select a directory')
        self.menuFileQuit = menuFile.Append(wx.ID_EXIT, u'&Quit\tCtrl+Q',
                                            u'Quit application')

        menuHelp = wx.Menu()
        #self.menuHelpHelp = menuHelp.Append(wx.ID_HELP, '&Help\tF1',
        #                                    'View Help files')
        self.menuHelpAbout = menuHelp.Append(wx.ID_ABOUT, u'&About',
                                        u'About this program')

        menuBar.Append(menuFile, title=u"&File")
        menuBar.Append(menuHelp, title=u"&Help")

        # Set up the basic sizer - all elements fit into this.
        sizer = wx.GridBagSizer(7,4)

        boxDropdowns = wx.BoxSizer(orient=wx.HORIZONTAL)
        textDelimiter = wx.StaticText(panel, label=u"Delimiter")
        boxDropdowns.Add(textDelimiter, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL,
                         border=5)
        boxDropdowns.Add(self._comboBoxDelimiter, flag=wx.LEFT, border=5)

        sizer.Add(boxDropdowns, pos=(0,0), flag=wx.TOP, border=5)

        helpDelimiter = wx.StaticText(
            panel,
            label=u"Determines the character used to separate words.")
        helpFlickr = wx.StaticText(
            panel,
            label=u"Replaces any filename from Flickr with its name from the site.")
        helpCapital = wx.StaticText(
            panel,
            label=u"Capitalizes the first letter of each word.")

        sizer.Add(helpDelimiter, pos=(0,1),
                  flag=wx.LEFT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer.Add(helpFlickr, pos=(2,1), flag=wx.LEFT, border=5)
        sizer.Add(helpCapital, pos=(3,1), flag=wx.LEFT, border=5)

        line = wx.StaticLine(panel)
        sizer.Add(line, pos=(1,0), span=(1,4), flag=wx.EXPAND)


        sizer.Add(self._checkboxFlickr, pos=(2,0),
                  flag=wx.LEFT, border=5)
        sizer.Add(self._checkboxCapital, pos=(3,0),
                  flag=wx.LEFT, border=5)

        sizer.Add(self._listRename, pos=(4,0), span=(1,4), flag=wx.EXPAND)

        boxPath = wx.BoxSizer(orient=wx.HORIZONTAL)
        labelPath = wx.StaticText(panel, label=u"Current Path")
        boxPath.Add(labelPath, flag=wx.LEFT|wx.ALIGN_CENTER_VERTICAL, border=5)
        boxPath.Add(self._textPath, proportion=1, flag=wx.EXPAND|wx.LEFT,
                    border=5)

        sizer.Add(boxPath, pos=(5,0), span=(1,2),
                  flag=wx.EXPAND|wx.LEFT|wx.BOTTOM, border=5)
        sizer.Add(self.buttonOpen, pos=(5,2),
                  flag=wx.LEFT|wx.BOTTOM, border=5)
        sizer.Add(self.buttonRename, pos=(5,3),
                  flag=wx.LEFT|wx.BOTTOM|wx.RIGHT, border=5)

        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(4)

        panel.SetSizer(sizer)

        self.SetMenuBar(menuBar)

        self.Centre()
        self.Show()

    def start(self):
        self.app = wx.App()
        self.app.MainLoop()

    def resizeColumns(self, width):
        self._listRename.SetColumnWidth(0, width)
        self._listRename.SetColumnWidth(1, width)

    def openDir(self, lastPath):
        dlg = DialogOpenFolder(self, defaultPath = lastPath)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            path = dlg.GetPath()
            self._lastPath = path
            return path
        return None

    def showError(self, title, message):
        dlg = wx.MessageDialog(None, message=message, title=title,
                               style=wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()

    def showInfo(self, title, message):
        dlg = wx.MessageDialog(None, message=message, caption=title,
                               style=wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def showConfirm(self, title, message):
        dlg = wx.MessageDialog(None, caption=title, message=message,
                               style=wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            return True
        return False

    def showProgress(self, progress, title = "", message = "", abort = False):
        """Creates a new progress dialog box, or updates an existing one.
        Returns False only if user selects Cancel."""
        if self._progress:
            if self._progress.Update(progress)[0]:
                return True
            return False
        else:
            if abort:
                style = wx.PD_AUTO_HIDE|wx.PD_CAN_ABORT
            else:
                style = wx.PD_AUTO_HIDE
            self._progress = wx.ProgressDialog(title=title, message=message,
                                               style=style)
            self._progress.Show()
            return True

    def stopProgress(self):
        if self._progress:
            self._progress.Update(100)
            self._progress.Destroy()
            return True
        return False

    def showHelpBox(self):
        pass

    def showAboutBox(self, version):
        description = u"""Image Rename is an automatic file renamer, done as a \
code structure test for a larger image-reference collage program."""

        info = wx.AboutDialogInfo()
        info.SetName(u"Ref Collage")
        info.SetVersion(version)
        info.SetDescription(description)
        info.SetDevelopers([u"David Edmondson"])

        wx.AboutBox(info)

    # Properties for getting / setting - necessary for translation to wx
    def enableButtonRename(self, state):
        if state:
            self.buttonRename.Enable()
        else:
            self.buttonRename.Disable()

    def _getListRename(self):
        """Returns two lists - first column, second column"""
        return self._listRename.GetColumn(0), self._listRename.GetColumn(1)

    def _setListRename(self, (oldList, newList)):
        # TODO: Allow custom sorting
        self._listRename.DeleteAllItems()
        # Sort first by path, then file
        for oldFn, newFn in zip(oldList, newList):
            pos = self._listRename.InsertStringItem(0, oldFn)
            self._listRename.SetStringItem(pos, 1, newFn)

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

    def _getTextPath(self):
        return self._textPath.GetLabel()

    def _setTextPath(self, text):
        self._textPath.SetLabel(text)

    rename = property(_getListRename, _setListRename)
    delimiter = property(_getComboBoxDelimiter, _setComboBoxDelimiter)
    delimiterOptions = property(_getDelimiterOptions, _setDelimiterOptions)
    flickr = property(_getCheckboxFlickr, _setCheckboxFlickr)
    capital = property(_getCheckboxCapital, _setCheckboxCapital)
    path = property(_getTextPath, _setTextPath)

if __name__ == "__main__":
    app = wx.App()
    view = View(parent=None)
    app.MainLoop()
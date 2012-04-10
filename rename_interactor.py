"""
Name        rename_interactor.py
Author      David Edmondson, adapted from sample by Peter Damoc

Interactor binds event handlers to the View, and calls methods in the Presenter,
which strips nearly all logic from the visual part of the UI.
"""

import wx

class Interactor(object):
    def install(self, presenter, view):
        self.presenter = presenter
        self.view = view
        self.view.Bind(wx.EVT_CLOSE, self.onQuit)
        self.view.Bind(wx.EVT_MENU, self.onQuit, self.view.menuFileQuit)
        self.view.Bind(wx.EVT_MENU, self.onOpenDir, self.view.menuFileOpen)
        # TODO: Get me some help!
        #self.view.Bind(wx.EVT_MENU, self.onOpenHelp, self.view.menuHelpHelp)
        self.view.Bind(wx.EVT_MENU, self.onOpenAbout, self.view.menuHelpAbout)
        self.view._comboBoxDelimiter.Bind(
            wx.EVT_COMBOBOX, self.onSettingChanged)
        self.view._checkboxFlickr.Bind(
            wx.EVT_CHECKBOX, self.onSettingChanged)
        self.view._checkboxCapital.Bind(
            wx.EVT_CHECKBOX, self.onSettingChanged)
        self.view.buttonOpen.Bind(
            wx.EVT_BUTTON, self.onOpenDir)
        self.view.buttonRename.Bind(
            wx.EVT_BUTTON, self.onRenameClicked)

    def onQuit(self, e):
        """Open a close program confirmation"""
        self.presenter.quit()

    def onOpenDir(self, e):
        """Open the Select Folder dialog."""
        self.presenter.openPath()

    def onRenameClicked(self, e):
        """Renames all displayed files."""
        self.presenter.renameFiles()

    def onSettingChanged(self, e):
        """Update model whenever settings are changed"""
        self.presenter.settingsChanged()

    def onOpenAbout(self, e):
        """Opens the About box."""
        self.presenter.openAbout()

    def onOpenHelp(self, e):
        """Opens the Help window."""
        self.presenter.openHelp()
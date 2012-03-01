"""
Name:       presenters.py
Author:     David Edmondson, adapted from wxPython example from Peter Damoc
"""

import socket

class Presenter(object):
    def __init__(self, model, interactor, view):
        self.model = model
        interactor.install(self, view)
        self.view = view
        self._initView()

    def _initView(self):
        """Loads settings from the model, and reflects this on the view."""
        settings = self.model.getSettings()
        self.view.delimiterOptions = self.model.DELIMITERS
        self.view.flickr = settings["flickr"]
        self.view.capital = settings["capital"]
        self.view.delimiter = settings["delimiter"]
        self.view.enableButtonRename(False)
        self.view.start()

    def onResize(self):
        """Resizes elements and columns as needed when the window is resized."""

    def openPath(self):
        """Opens a wx.DirDialog box to select a directory."""

        lastPath = self.model.getSettings()["lastPath"]
        # TODO: save the default path between sessions
        path = self.view.openDir(lastPath)

        if not path:
            return None

        try:
            renameList = self.model.getRenameList(path)
        except socket.error:
            error = "Cannot connect to flickr.com. Disable the Flickr option \
to continue without Flickr name lookup, or try again later."
            self.view.showError(error)
            return None

        self._updateRenameList(renameList)

    def _updateRenameList(self, renameList):
        # Strip off the path for presentation
        #index = len(path) + 1
        #renameList = {
        #    oldFn[index:] : newFn[index:] for oldFn, newFn in renameList.items()
        #}

        if not renameList:
            renameList = {"No files to rename in selected path.":""}
            self.view.enableButtonRename(False)
        else:
            self.view.enableButtonRename(True)
        self.view.rename = renameList

    def quit(self):
        """Opens a confirmation window. Exits the application if Yes."""
        confirm = self.view.showConfirm(
            "Confirm Quit", "Are you sure you want to quit?")
        if confirm:
            self.view.Destroy()

    def about(self):
        """Opens a confirmation window. Exits the application if Yes."""

    def settingsChanged(self):
        """Passes preferences onto the Model for validation and saving."""
        result = {
            "flickr": self.view.flickr,
            "capital": self.view.capital,
            "delimiter": self.view.delimiter
        }
        renameList = self.model.changeSettings(result)
        if renameList:
            self._updateRenameList(renameList)

    def renameFiles(self):
        """Halts UI interaction, and informs the Model to run its current
        rename queue."""
        confirm = self.view.showConfirm(
            "Confirm Rename",
            "Rename files?"
        )
        if not confirm:
            return None
        try:
            numRename = self.model.renameFiles()
            self.view.showInfo(
                "Rename Successful",
                "{} files renamed successfully.".format(numRename)
            )
        except (IOError, WindowsError) as e:
            self.view.showError(
                "Error occurred during rename: \n{}".format(e))
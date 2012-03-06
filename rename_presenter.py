"""
Name:       presenters.py
Author:     David Edmondson, adapted from wxPython example from Peter Damoc
"""

import socket, time
from threading import Thread

class threadModelInterrupt(Thread):
    def stop(self, model):
        """Notify the model to interrupt its current action."""
        model.interrupt = True

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
        self.view.resizeColumns(370)
        self.view.start()

    def resizeCols(self, width):
        """Resizes elements and columns as needed when the window is resized."""
        colWidth = (width - 60) // 2
        self.view.resizeColumns(colWidth)

    def openPath(self):
        """Opens a wx.DirDialog box to select a directory."""

        # Checking to allow automatic updates of rename list on setting.
        # Auto updates are quick because of Flickr name caching.
        lastPath = self.model.getSettings()["lastPath"]
        path = self.view.openDir(lastPath)
        if not path:
            return None
        self._getRenameList(path)

    def _getRenameList(self, path):
        worker = threadModelInterrupt(target=self.model.createRenameList,
                                    args=(path, ))
        worker.start()
        # Main progress loop
        try:
            self.view.showProgress(0, "Please Wait...",
                                   "Generating rename list...")
            while True:
                # Continue progress-update loop until 100% done, or interrupted
                if self.model.progress == 100:
                    self.model.progress = 0.0
                    self.view.stopProgress()
                    renameList = self.model.getRenameList()
                    break
                if not self.view.showProgress(self.model.progress):
                    self.model.progress = 0.0
                    self.view.stopProgress()
                    worker.stop(self.model)
                    renameList = None
                    break
                time.sleep(0.1)
        except socket.error:
            error = "Cannot connect to flickr.com. Disable the Flickr option \
to continue without Flickr name lookup, or try again later."
            self.view.showError("Error", error)
            renameList = None

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

    def settingsChanged(self):
        """Passes preferences onto the Model for validation and saving."""
        result = {
            "flickr": self.view.flickr,
            "capital": self.view.capital,
            "delimiter": self.view.delimiter
        }
        openedPath = self.model.changeSettings(result)
        if openedPath:
            self._getRenameList(openedPath)

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

    def openHelp(self):
        self.view.showHelpBox()

    def openAbout(self):
        self.view.showAboutBox()
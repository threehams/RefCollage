"""
Name        rename_presenter.py
Author      David Edmondson, adapted from sample by Peter Damoc

Receives commands from the Interactor based on user input.
Pulls data from the Model through its API, threading if necessary, and prepares
and pushes it to the View through its API.

No data should ever be stored in the Presenter; it should always be pulled from
the Model's API.

No wx-specific methods should be called directly from the Presenter - it should
know nothing about the UI itself.
"""


import socket, time, os
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
            self.view.showProgress(0, title=u"Please Wait...",
                                   message=u"Generating rename list...",
                                   abort=True)
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
        except (socket.error, IOError):
            error = u"Cannot connect to flickr.com. Disable the Flickr option \
to continue without Flickr name lookup, or try again later."
            self.view.showError(u"Error", error)
            renameList = None

        self._updateRenameList(renameList)

    def _updateRenameList(self, renameList):
        path = self.model.getSettings()["lastPath"]
        if not renameList:
            old = [u"No files to rename in path:"]
            new = [path]
            self.view.enableButtonRename(False)
            self.view.rename = (old, new)
            return None

        self.view.enableButtonRename(True)

        old, new = [], []
        renameKeys = sorted(renameList.keys(),
                            key=lambda k: (k.rsplit(os.sep)[0], k.lower()),
                            reverse=True)

        pathLen = len(path) + 1
        for key in renameKeys:
            old.append(key[pathLen:])
            new.append(renameList[key][pathLen:])

        self.view.rename = (old, new)
        self.view.path = path

    def quit(self):
        """Opens a confirmation window. Exits the application if Yes."""
        confirm = self.view.showConfirm(
            u"Confirm Quit", u"Are you sure you want to quit?")
        if confirm:
            self.view.Destroy()

    def settingsChanged(self):
        """Passes preferences onto the Model for validation and saving."""
        result = {
            "flickr":    self.view.flickr,
            "capital":   self.view.capital,
            "delimiter": self.view.delimiter
        }
        openedPath = self.model.changeSettings(result)
        if openedPath:
            self._getRenameList(openedPath)

    def renameFiles(self):
        """Halts UI interaction, and informs the Model to run its current
        rename queue."""
        confirm = self.view.showConfirm(
            u"Confirm Rename",
            u"Rename files?"
        )
        if not confirm:
            return None
        try:
            numRename = self.model.renameFiles()
            self.view.showInfo(
                u"Rename Successful",
                u"{} files renamed successfully.".format(numRename)
            )
        except (IOError, WindowsError) as e:
            self.view.showError(
                u"Error occurred during rename: \n{}".format(e))

    def openHelp(self):
        self.view.showHelpBox()

    def openAbout(self):
        self.view.showAboutBox(self.model.version)
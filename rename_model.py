"""
    Model handles all logic for data, with a limited set of public commands,
    and can be used without an interface for testing or alternative control
    (command-line).

    getRenameList(path)
        Traverses the given directory recursively, and returns a dictionary.
        Keys are original names, values are modified names.

    renameFiles():
        Processes the current list of files.

    setOptions():
        Updates the model with current settings.

    Options:
    Delimiter       Use [ _-] as a delimiter between words.
    Title           Capitalize the first letter of each word.
    Flickr          If a Flickr image filename is detected, this will attempt
                    to replace the filename with the image title. Check done
                    via http://flickr.com/photo.gne?id=[ID]

"""

import httplib
import os, re, logging, json

class Model(object):

    # File locations
    APPDATA_ROOT = os.path.join(os.environ["APPDATA"], "ThreeHams", "RefCollage")
    FILE_SETTINGS = os.path.join(APPDATA_ROOT, "settings.cfg")
    FILE_MEMO_FLICKR = os.path.join(APPDATA_ROOT, "memoFlickr.cfg")
    FILE_LOG_ERROR = os.path.join(APPDATA_ROOT, "error.log")

    SETTING_DEFAULT = {
        "delimiter":" ",
        "flickr":False,
        "capital":False,
        "lastPath":""}

    IMAGE_EXTENSIONS = (".jpg",".jpeg",".png",".bmp",".tif",".tiff",".tga")
    DELIMITERS = (" ","_","-",".")

    # Local memos
    memoFlickr = {}

    def __init__(self):
        """Initialize options to defaults."""
        self._loadSettings()

        self._renameList = {}
        self._checkDirs()
        self._loadMemoFlickr()
        self._openedPath = False

    def changeSettings(self, settings):
        # TODO: Merge duplicated code. Problem: internal vs external method
        if settings["delimiter"] not in Model.DELIMITERS:
            raise TypeError("invalid delimiter: {}".format(settings["delimiter"]))

        self._flickr = settings["flickr"]
        self._capital = settings["capital"]
        self._delimiter = settings["delimiter"]
        self._saveSettings()
        if self._openedPath:
            return self.getRenameList(self._lastPath)

    def getSettings(self):
        settings = {
            "flickr":self._flickr,
            "capital":self._capital,
            "delimiter":self._delimiter,
            "lastPath":self._lastPath
        }
        return settings

    def _loadSettings(self):
        f = open(Model.FILE_SETTINGS, "r")
        try:
            settings = json.load(f)
        except ValueError:
            logging.warning("no settings data found, starting from scratch")
            settings = Model.SETTING_DEFAULT
        f.close()
        # TODO: Merge duplicated code. Problem: internal vs external method
        self._flickr = settings["flickr"]
        self._capital = settings["capital"]
        self._delimiter = settings["delimiter"]
        try:
            self._lastPath = settings["lastPath"]
        except KeyError:
            self._lastPath = ""

    def _saveSettings(self):
        settings = {
            "flickr":self._flickr,
            "capital":self._capital,
            "delimiter":self._delimiter,
            "lastPath":self._lastPath
        }
        f = open(Model.FILE_SETTINGS, "w+")
        json.dump(settings, f)
        f.close()

    def getRenameList(self, path):
        """Gets a list of image files, and constructs a dictionary-based rename
        queue based on current settings."""
        self._lastPath = path
        self._saveSettings()

        self._renameList = {}
        structure = os.walk(path)
        for root, _, files in structure:
            for fn in files:
                # Ignore any non-image files
                if not self._isImage(fn):
                    continue
                flickrId = self._isFlickr(fn)
                if flickrId:
                    newFn = self._getNameFlickr(fn, flickrId)
                else:
                    newFn = self._convertName(fn)

                # Ignore if the filename is the same - but still have to check
                # for duplicates
                nameWithPath = os.path.join(root, newFn)
                dupeName = self._checkDuplicates(nameWithPath)
                if fn == newFn and not dupeName:
                    continue
                elif dupeName:
                    newFn = dupeName
                else:
                    newFn = nameWithPath

                self._renameList[os.path.join(root, fn)] = newFn
        self._saveMemoFlickr()
        # Enable automatic updating of names on setting changes
        self._openedPath = True
        return self._renameList

    def renameFiles(self):
        """Validates the rename list and processes. Returns the number of files
        renamed."""
        for oldFn, newFn in self._renameList.items():
            os.rename(oldFn, newFn)
        return len(self._renameList)

    def _checkDuplicates(self, fn):
        """Check for duplicate path+name. Returns a new name if found,
        None if not."""
        i = 0
        newFn = fn
        while newFn in self._renameList.values():
            i += 1
            strSplit = fn.rsplit(".", 1)
            strSplit[0] += " ({})".format(i)
            newFn = '.'.join(strSplit)
        if i:
            return newFn
        return None

    def _checkDirs(self):
        """Check if directories and files exist - create if necessary."""
        if not os.path.isdir(Model.APPDATA_ROOT):
            os.makedirs(Model.APPDATA_ROOT)
        for fn in (
            Model.FILE_SETTINGS,
            Model.FILE_LOG_ERROR,
            Model.FILE_MEMO_FLICKR
        ):
            if not os.path.isfile(fn):
                open(fn, "w+b").close()


    def _loadMemoFlickr(self):
        """Loads the cached Flickr name list from disk."""
        f = open(Model.FILE_MEMO_FLICKR, "r")
        try:
            memoFlickr = json.load(f)
            Model.memoFlickr = memoFlickr
        except ValueError:
            logging.warning("no valid Flickr memo data found, starting from scratch")
        f.close()

    def _saveMemoFlickr(self):
        """Saves the cached Flickr name list to disk."""
        f = open(Model.FILE_MEMO_FLICKR, "w+")
        json.dump(Model.memoFlickr, f)
        f.close()

    def _isImage(self, fn):
        if fn.lower().endswith(Model.IMAGE_EXTENSIONS):
            return True
        return False

    def _isFlickr(self, fn):
        """ Checks if the filename fits the Flickr naming convention:
         ID (numbers), underscore, numbers + a-f, underscore.
         Returns ID if found, False if not.

         This will also catch Flickr names which have leading or trailing
         characters."""

        if not self._flickr:
            return False

        if not fn.lower().endswith(Model.IMAGE_EXTENSIONS):
            return False

        # Grab the ID while we're checking if it matches
        result = re.search(r"([0-9].*)_[0-9a-f].*\.", fn.lower())
        if result:
            return result.group(1)
        return False

    def _getRedirect(self, site, page):
        """Gets the 'location' header to avoid redirection."""
        conn = httplib.HTTPConnection(site)
        conn.request("HEAD", page)
        response = conn.getresponse()

        # Strip off trailing slash, or httplib won't retrieve data!
        location = response.getheader("location")
        conn.close()

        if location:
            return location.rstrip("/")

        return None

    def _getNameFlickr(self, fn, flickrId):
        """Opens a connection to Flickr, gets the title of the page loaded,
        removes all characters except [0-9a-Z_-], and clips the title to the
        first five words or 30 characters (whichever is smaller). Returns a
        valid filename with extension.

        Example: http://flickr.com/photo.gne?id=6795654383"""

        if flickrId in Model.memoFlickr:
            return self._convertName(Model.memoFlickr[flickrId])

        # Grab the redirect from the header. 404? Return converted filename
        location = self._getRedirect("flickr.com", "/photo.gne?id=" + flickrId)
        # If 404 or private page - return converted original name
        if (not location) or ("signin" in location):
            return self._convertName(fn)

        # Grab only the first part of the site find the title
        conn = httplib.HTTPConnection("www.flickr.com")
        conn.request("GET", location)
        res = conn.getresponse()
        title = res.read(350)
        conn.close()

        # Take the title from the
        title = re.search(r"<title>(.*) \| Flickr.*</title>", title).group(1)

        # Strip off everything except [0-9a-Z_-]
        title = re.sub("[^\w _-]", "", title)

        # Get extension from original name
        ext = "." + fn.rsplit(".", 1)[1].lower()

        # Memoize the name BEFORE conversion to allow conversion later.
        Model.memoFlickr[flickrId] = title + ext
        return self._convertName(title + ext)

    def _convertName(self, fn):
        """Returns a new name by removing and replacing common punctuation,
        then applying other modifications based on settings. Extensions
        are always converted to lowercase."""
        if not self._isImage(fn):
            raise TypeError("file " + str(fn) + " is not an image")

        # Extract the extension, lower() it, and save it for later.
        try:
            baseName, ext = fn.rsplit(".", 1)
            ext = "." + ext.lower()
        except IndexError:
            raise TypeError("filename " + str(fn) + " does not contain an extension!")

        # Strip leading and trailing delimiters, then replace others
        baseName = re.sub("[. _-]+", self._delimiter, baseName.strip("_- ."))
        if self._capital:
            baseName = baseName.title()
        return baseName + ext
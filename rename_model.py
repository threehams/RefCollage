"""
Name        rename_model.py
Author      David Edmondson, adapted from sample by Peter Damoc

Model handles all logic for data, with a limited set of public commands, and
can be used without an interface for testing or alternative control (command-
line).

Settings:
Delimiter   Use [ _-.] as a delimiter between words.
Title       Capitalize the first letter of each word.
Flickr      If a Flickr image filename is detected, this will attempt to replace
            the filename with the image title. Check done via:
            http://flickr.com/photo.gne?id=[ID]

"""

import httplib
import os, re, logging, json

class Model(object):
    # File locations
    APPDATA_ROOT = os.path.join(os.environ["APPDATA"], "ThreeHams", "RefCollage")
    FILE_SETTINGS = os.path.join(APPDATA_ROOT, "settings.cfg")
    FILE_MEMO_FLICKR = os.path.join(APPDATA_ROOT, "memoFlickr.cfg")
    FILE_LOG_ERROR = os.path.join(APPDATA_ROOT, "error.log")
    FLICKR_REGEX = re.compile(r"([0-9]{6,10})_[0-9a-f]{6,10}[._]")

    SETTING_DEFAULT = {
        "delimiter":" ",
        "flickr":False,
        "capital":False,
        "lastPath":""}

    IMAGE_EXTENSIONS = (".jpg",".jpeg",".png",".bmp",".tif",".tiff",".tga",
                        ".gif")
    DELIMITERS = (" ","_","-",".")

    # Local memos
    memoFlickr = {}

    def __init__(self):
        self._loadSettings()

        self._renameList = {}
        self._checkDirs()
        self._loadMemoFlickr()
        self._openedPath = False

        self.interrupt = False
        self.progress = 0.0
        self.version = "0.53"

        logging.basicConfig(filename=Model.FILE_LOG_ERROR,level=logging.WARNING)

    def changeSettings(self, settings):
        """Validate settings from the presenter and save.

        If a directory has already been selected, this returns the current path,
        so the presenter can handle UI for retrieval of the new rename list."""

        if settings["delimiter"] not in Model.DELIMITERS:
            raise ValueError("invalid delimiter: {}".format(settings["delimiter"]))

        self._flickr = settings["flickr"]
        self._capital = settings["capital"]
        self._delimiter = settings["delimiter"]
        self._saveSettings()

        if self._openedPath:
            return self._lastPath

    def getSettings(self):
        settings = {
            "flickr":self._flickr,
            "capital":self._capital,
            "delimiter":self._delimiter,
            "lastPath":self._lastPath}
        return settings

    def _validateSetting(self, name, settings, arrayCheck = None,
                         default = None, instance = None):
        """Validates a setting. If validation fails, returns default if available,
        then arrayCheck[0], then None if neither are available"""
        try:
            if instance and isinstance(settings[name], instance):
                return settings[name]
            if arrayCheck and settings[name] in arrayCheck:
                return settings[name]
        except KeyError:
            pass

        logging.warning(
            "invalid setting found for {}, setting to default".format(name))
        if default is not None:
            return default
        if arrayCheck:
            return arrayCheck[0]

    def _loadSettings(self):
        try:
            f = open(Model.FILE_SETTINGS, "r")
            settings = json.load(f)
            f.close()
        except (IOError, ValueError):
            logging.warning("no settings data found, starting from scratch")
            settings = Model.SETTING_DEFAULT

        # Validate settings before blindly accepting!

        self._flickr = self._validateSetting(
            "flickr", settings, arrayCheck=(False, True))
        self._capital = self._validateSetting(
            "capital", settings, arrayCheck=(False, True))
        self._delimiter = self._validateSetting(
            "delimiter", settings, arrayCheck=Model.DELIMITERS)
        self._lastPath = self._validateSetting(
            "lastPath", settings, instance=basestring, default="")
        self._saveSettings()

    def _saveSettings(self):
        settings = {
            "flickr":self._flickr,
            "capital":self._capital,
            "delimiter":self._delimiter,
            "lastPath":self._lastPath}
        f = open(Model.FILE_SETTINGS, "w+")
        json.dump(settings, f)
        f.close()

    def createRenameList(self, path):
        """Gets a list of image files, and constructs a dictionary-based rename
        queue based on current settings."""
        self._lastPath = path
        self._saveSettings()
        self._renameList = {}

        self.progress = 0.0
        progress = 0.0

        walkLen = 0
        # Find the total length of the walk, so we can get accurate progress.
        for _, _, files in os.walk(path):
            walkLen += len(files)

        for root, _, files in os.walk(path):
            for fn in files:
                # Max out at 99.9% progress until completely done.
                progress += 1
                self.progress = (progress / walkLen) * 100 - .01

                # Stop on thread interrupt
                if self.interrupt:
                    self._saveMemoFlickr()  # Keep Flickr progress!
                    self._renameList = {}   # Don't allow a partial rename list
                    self.interrupt = False
                    return

                # Ignore any non-image files
                if not self._isImage(fn):
                    continue

                flickrId = self._isFlickr(fn)
                if flickrId:
                    try:
                        newFn = self._getNameFlickr(fn, flickrId)
                    except:
                        self._saveMemoFlickr()
                        raise
                else:
                    newFn = self._convertName(fn)

                # Ignore if the filename is the same - but still have to check
                # for duplicates (edge cases).
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
        self.progress = 100

    def getRenameList(self):
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
            Model.FILE_MEMO_FLICKR):
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

        if not fn.lower().endswith((".jpg",".jpeg")):
            return False

        # Grab the ID while we're checking if it matches
        result = Model.FLICKR_REGEX.search(fn.lower())
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

    def _getNameFlickr(self, fn, flickrId, retry = 0):
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
        numChars = 300 + (retry * 50)
        title = res.read(numChars)
        conn.close()

        if "no longer active" in title or "Please wait" in title:
            return self._convertName(fn)
        if retry > 0:
            logging.warning("Failed title: {}".format(title))
        # Split the title from the page
        title = re.search(r"<title>(.*) \| Flickr.*</title>", title)
        if title is None:
            if retry < 3:
                logging.warning("Flickr name retrieval failed, retrying.")
                return self._getNameFlickr(fn, flickrId, retry + 1)
            else:
                raise IOError("could not retrieve name from Flickr.com")

        else:
            title = title.group(1)
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
        baseName, ext = fn.rsplit(".", 1)
        ext = "." + ext.lower()

        # Strip leading and trailing delimiters, then replace others
        baseName = re.sub("[. _-]+", self._delimiter, baseName.strip("_- ."))
        if self._capital:
            baseName = baseName.title()
        return baseName + ext
"""
Name        rename.py
Author      David Edmondson

Traverses a directory, and normalizes names, based on settings given by the
user.

Modules:
Model       Handles all data and data logic for the program. The model is
            capable of handling all rename queues and operations without
            presenter or view attached, and can be tested separately. This also
            allows it to be driven by command-line with another module.
Presenter   Receives commands from the Interactor, pulls data from the Model
            through its API, and converts data to a form usable by the View.
            No data is ever stored in the Presenter - it is always pulled from
            the Model.
Interactor  Works as an extension of the presenter, binding event handlers to
            the View, and calling Presenter methods.
View        Handles all wx-specific code, but contains an absolute minimum of
            logic - strictly converts wx language to something friendlier to
            Python. View should only ever be asked for user-entered data, which
            is validated by the Model.

Test Cases:
Model       Tests model functionality without presenter or view attached.
Presenter   Tests presenter and model interaction, but uses a mock object for
            the view, which strips it of all wx functionality.
Objects     Contains mock objects which contain the required methods for
            testing, but have no UI functionality.

            Both test suites create temporary directories using the TEMP
            environment variable, using platform-independent functions.
"""
import wx


from rename_model import Model
from rename_presenter import Presenter
from rename_interactor import Interactor
from rename_view import View

if __name__ == "__main__":
    app = wx.App()
    view = View(parent=None)
    model = Model()
    interactor = Interactor()
    presenter = Presenter(model, interactor, view)
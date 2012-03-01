"""
    Traverses a directory, and normalizes names.


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
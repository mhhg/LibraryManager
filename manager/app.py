import wx
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "elm.settings"
import django

django.setup()

from django.template.loader import render_to_string
from notebook import TestNB
import sys


class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.SetSize((840, 580))
        nb = TestNB(self, -1, sys.stderr)
        nb.SetFocus()


class MainApplication(wx.App):
    def __init__(self, *args, **kwargs):
        wx.App.__init__(self, *args, **kwargs)
        self.frame = MainFrame(None, -1, "ELA Library Manager", pos=(0  , 0),
                               size=(200, 100),
                               style=wx.DEFAULT_FRAME_STYLE,
                               name="run a sample")
        self.SetTopWindow(self.frame)
        self.frame.Show(True)

    def OnInit(self):

        return True


def elm():
    try:
        app = MainApplication(redirect=False, useBestVisual=True)
        app.MainLoop()
    except Exception, e:
        print e


from wx.html import HtmlEasyPrinting



def tmp():
    s = render_to_string('invoice.html', context={'name': 'Amir'})
    print s
    return s


from xhtml2pdf import pisa  # import python module

# Define your data
outputFilename = "test.pdf"

# Utility function
def convertHtmlToPdf(sourceHtml, pdf_file_name):
    # open output file for writing (truncated binary)

    pdf = open(pdf_file_name, "w+b")

    # convert HTML to PDF
    pisaStatus = pisa.CreatePDF(sourceHtml, dest=pdf)

    # close output file
    pdf.close()  # close output file

    # return True on success and False on errors
    return pisaStatus.err


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        # self.lst = wx.ListCtrl(self, wx.ID_ANY, size=(400, 400),
        #                        style=wx.LC_REPORT)
        # self.lst.InsertColumn(0, "ID")
        # self.lst.InsertColumn(1, "Title")
        # self.lst.InsertColumn(2, "Serial")
        # for i, b in enumerate(Book.objects.all()):
        #     self.lst.Append([str(i), b.title, str(b.serial)])
        #     self.lst.SetItemData(i, b.pk)


if __name__ == "__main__":
    # from dialogs import Printer
    from manager.models import Book
    # elm()
    # inv = Invoice.objects.get(pk=2)
    # logo = r"C:\Ela_Library_Manager\manager\ela.bmp"
    # s = render_to_string('invoice.html', context={'invoice': inv,
    # 'logo':logo})
    # convertHtmlToPdf(s, outputFilename)

    # s = tmp()
    # print inv.items.all()
    # print s
    # pisa.showLogging()
    # app = wx.App(useBestVisual=True)
    # frame = MyFrame(None, -1, "Test DC")
    # frame.Show(True)
    # app.MainLoop()
    elm()
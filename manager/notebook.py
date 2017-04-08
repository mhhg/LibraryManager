
import  sys

import wx


import book_list
import invoice_list

import wx.html as html



class TestNB(wx.Notebook):
    def __init__(self, parent, id, log):
        self.parent = parent
        wx.Notebook.__init__(self, parent, id, size=(21,21), style=
        wx.BK_DEFAULT
                             #wx.BK_TOP 
                             #wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
                             # | wx.NB_MULTILINE
        )
        self.log = log

        # win = self.makeColorPanel(wx.BLUE)
        # self.AddPage(win, "Blue")
        # st = wx.StaticText(win.win, -1,
        #                    "You can put nearly any type of window here,\n"
        #                    "and if the platform supports it then the\n"
        #                    "tabs can be on any side of the notebook.",
        #                    (10, 10))

        # st.SetForegroundColour(wx.WHITE)
        # st.SetBackgroundColour(wx.BLUE)

        # Show how to put an image on one of the notebook tabs,
        # first make the image list:
        # il = wx.ImageList(16, 16)
        # idx1 = il.Add(images.Smiles.GetBitmap())
        # self.AssignImageList(il)

        # now put an image on the first tab we just created:
        # self.SetPageImage(0, idx1)


        # win = self.makeColorPanel(wx.RED)
        # self.AddPage(win, "Red")

        # win = ScrolledWindow.MyCanvas(self)
        # self.AddPage(win, 'ScrolledWindow')
        #
        # win = self.makeColorPanel(wx.GREEN)
        # self.AddPage(win, "Green")
        #
        # win = GridSimple.SimpleGrid(self, log)
        # self.AddPage(win, "Grid")
        #


        self.book_panel = book_list.BookPanel(self, log)
        self.AddPage(self.book_panel, 'Books')
        self.invoice_panel = invoice_list.InvoicePanel(self, log)
        self.AddPage(self.invoice_panel, 'Invoices')

        # win = ListCtrl.TestListCtrlPanel(self, log)
        # self.AddPage(win, 'List')
        # win = ListCtrl.TestListCtrlPanel(self, log)
        # self.AddPage(win, 'List')
        # win = ListCtrl.TestListCtrlPanel(self, log)
        # self.AddPage(win, 'List')


        # win = self.makeColorPanel(wx.CYAN)
        # self.AddPage(win, "Cyan")
        #
        # win = self.makeColorPanel(wx.NamedColour('Midnight Blue'))
        # self.AddPage(win, "Midnight Blue")
        #
        # win = self.makeColorPanel(wx.NamedColour('Indian Red'))
        # self.AddPage(win, "Indian Red")

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)


    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        self.log.write('OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel))
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        self.log.write('OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel))
        event.Skip()
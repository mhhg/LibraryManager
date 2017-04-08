# -*- coding: utf-8 -*-
import os
import wx

os.environ["DJANGO_SETTINGS_MODULE"] = "elm.settings"

import django

django.setup()
from manager.models import Invoice
from manager.models import Book
from copy import deepcopy
from django.contrib.humanize.templatetags.humanize import intcomma
from datetime import datetime
from manager.models import InvoiceItem
from wx.lib.mixins.listctrl import CheckListCtrlMixin
import wx.lib.mixins.listctrl as listmix
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from elm.settings import BASE_DIR
have_package = True
try:
    import fitz
except ImportError:
    try:
        import PyPDF2
    except ImportError:
        try:
            import pyPdf
        except ImportError:
            have_package = False

if have_package:
    from wx.lib.pdfviewer import pdfViewer, pdfButtonPanel

_title, _no, _price = range(3)
columns = {
    _title: "Title",
    _no: "No",
    _price: "Price",
}


class PrintDialog(wx.Dialog):
    def __init__(self, parent, pdf_path):
        wx.Dialog.__init__(self, parent, -1, size=(600, 700),
                           style=wx.RESIZE_BORDER | wx.DEFAULT_DIALOG_STYLE)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        self.btn_panel = pdfButtonPanel(self, wx.NewId(),
                                        wx.DefaultPosition, wx.DefaultSize, 0)
        vsizer.Add(self.btn_panel, 0,
                   wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT |
                   wx.TOP,
                   5)
        self.viewer = pdfViewer(self, wx.NewId(), wx.DefaultPosition,
                                wx.DefaultSize,
                                wx.HSCROLL | wx.VSCROLL | wx.SUNKEN_BORDER)
        vsizer.Add(self.viewer, 1, wx.GROW | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        # loadbutton = wx.Button(self, wx.NewId(), "Load PDF file",
        # wx.DefaultPosition, wx.DefaultSize, 0 )
        # vsizer.Add(loadbutton, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        hsizer.Add(vsizer, 1, wx.GROW | wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        self.SetSizer(hsizer)
        self.SetAutoLayout(True)

        # introduce buttonpanel and viewer to each other
        self.btn_panel.viewer = self.viewer
        self.viewer.buttonpanel = self.btn_panel

        wx.BeginBusyCursor()
        self.viewer.LoadFile(pdf_path)
        wx.EndBusyCursor()


class BookListCtrl(wx.ListCtrl, listmix.TextEditMixin):
    def __init__(self, parent, ID, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0):
        self.parent = parent
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.TextEditMixin.__init__(self)

    def SetStringItem(self, i, col, data):

        if not self.parent.list_populated:
            wx.ListCtrl.SetStringItem(self, i, col, data)
            return
        pk = self.GetItemData(i)
        try:
            if col == _no:
                no = int(data)
                b = Book.objects.get(pk=pk)
                if b.no < no:
                    wx.MessageBox(
                        "We do not have enough %s in our Library. no "
                        "available %d" % (
                            b.title, b.no),
                        "Not Enough books!")
                    return
                wx.ListCtrl.SetStringItem(self, i, col, data)
                self.parent.update_no_array()
        except ValueError:
            wx.MessageBox(
                "Invalid value '%s' for column '%s'" % (data, columns[col]),
                "Invalid Value!")
            return


class InvoiceDialog(wx.Dialog):
    def __init__(self, *args, **kwargs):
        self.parent = kwargs["parent"]
        wx.Dialog.__init__(self, *args, **kwargs)
        size = (150, -1)
        self.first_name_txt = wx.TextCtrl(self, size=size)
        self.last_name_txt = wx.TextCtrl(self, size=size)
        self.date_txt = wx.TextCtrl(self, size=size)
        self.lst = BookListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT)
        self.total_price_lbl = wx.StaticText(self, label="0.0")
        self.save_btn = wx.Button(self, wx.ID_SAVE)
        self.cancel_btn = wx.Button(self, wx.ID_CANCEL)
        self.print_btn = wx.Button(self, wx.ID_PRINT)
        self.checked = deepcopy(self.parent.checked)
        self.seller = Invoice.OTHER
        size = (40, -1)
        self.no_array = {}
        self.date_txt.SetValue(str(datetime.now()))
        self._bind()
        self._do_layout()
        self.list_populated = False
        self._populate_book_lst()
        self.lst.SetItemState(0, wx.LIST_STATE_SELECTED,
                              wx.LIST_STATE_SELECTED)
        self.save_btn.Disable()
        self.print_btn.Disable()
        self.inv = None

    def _bind(self):
        self.save_btn.Bind(wx.EVT_BUTTON, self.OnSaveBtnClick)
        self.print_btn.Bind(wx.EVT_BUTTON, self.OnPrintBtnClick)
        self.lst.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.OnBeginEdit)
        self.first_name_txt.Bind(wx.EVT_TEXT, self.OnFirstNameTextChange)
        self.last_name_txt.Bind(wx.EVT_TEXT, self.OnLastNameTextChange)

    def OnFirstNameTextChange(self, event):
        self.toggle_save_btn()

    def OnLastNameTextChange(self, event):
        self.toggle_save_btn()

    def convertHtmlToPdf(self, sourceHtml, pdf_file_name):
        pdf = open(pdf_file_name, "w+b")
        pisaStatus = pisa.CreatePDF(sourceHtml, dest=pdf)
        pdf.close()
        return pisaStatus.err


    def toggle_save_btn(self):
        if self.first_name_txt.GetValue() != "" and \
                        self.last_name_txt.GetValue() != "":
            self.save_btn.Enable()
            self.print_btn.Enable()
        else:
            self.print_btn.Disable()
            self.save_btn.Disable()

    def OnBeginEdit(self, event):
        if event.GetColumn() != _no:
            event.Veto()
        else:
            event.Allow()

    def OnPrintBtnClick(self, evt):
        self.OnSaveBtnClick(evt)
        logo = os.path.join(BASE_DIR,  'manager', 'ela.bmp')
        s = render_to_string('invoice.html', context={'invoice': self.inv,
        'logo':logo})
        pdf_path = os.path.join(BASE_DIR,  'manager', 'invoice.pdf')
        self.convertHtmlToPdf(s, pdf_path)
        p = PrintDialog(self, pdf_path)
        p.Show()

    def update_no_array(self):
        self.no_array.clear()
        for i in range(self.lst.GetItemCount()):
            pk = self.lst.GetItemData(i)
            no = self.lst.GetItemText(i, _no)
            self.no_array[pk] = int(no)
        self.update_total_cost()

    def OnSaveBtnClick(self, evt):
        bfn = self.first_name_txt.GetValue()
        bln = self.last_name_txt.GetValue()
        books = Book.objects.filter(pk__in=self.checked)
        seller = self.seller
        date = str(self.date_txt.GetValue())
        print date
        inv = Invoice(buyer_first_name=bfn, buyer_last_name=bln,
                      seller=seller, date=date)
        inv.save()
        for b in books:
            no = self.no_array.get(b.pk, 1)
            InvoiceItem(invoice=inv, book=b, no=no).save()

        self.inv = inv

        wx.MessageBox("Invoice Successfully Saved!")

    def update_total_cost(self):
        t = 0
        for b in Book.objects.filter(pk__in=self.checked):
            t += self.no_array.get(b.pk, 1) * b.price

        self.total_price_lbl.SetLabelText(str(t) + ' Rial     ' +
                                          str(intcomma(
                                              int(t) / 10)) + ' Toman')

    def _populate_book_lst(self):
        self.list_populated = False
        self.lst.ClearAll()
        self.lst.InsertColumn(0, "Title")
        self.lst.InsertColumn(1, "No")
        self.lst.InsertColumn(2, "Price")
        for i, b in enumerate(Book.objects.filter(pk__in=self.checked)):
            self.lst.Append([b.title, str(1), str(b.price)])
            self.lst.SetItemData(i, b.pk)

        self.lst.SetColumnWidth(0, 170)
        self.lst.SetColumnWidth(1, 30)
        self.list_populated = True
        self.update_total_cost()

    def _do_layout(self):
        ms = wx.BoxSizer(wx.VERTICAL)

        sz = (520, -1)
        five = 5
        ten = 10
        a, e, l, t, r, b, acv, h, v = wx.ALL, wx.EXPAND, wx.LEFT, wx.TOP, \
                                      wx.RIGHT, wx.BOTTOM, \
                                      wx.ALIGN_CENTER_VERTICAL, \
                                      wx.HORIZONTAL, wx.VERTICAL
        ach = wx.ALIGN_CENTER_HORIZONTAL
        # buyer sizer
        bys = wx.StaticBoxSizer(wx.StaticBox(self, label="Buyer", size=sz), h)
        bys.Add(wx.StaticText(self, label="First Name:"), 0, l | acv, five)
        bys.Add(self.first_name_txt, 0, a, ten)
        bys.Add(wx.StaticText(self, label="Last Name:"), 0, l | acv, 50)
        bys.Add(self.last_name_txt, 0, a, ten)

        # book sizer
        bks = wx.StaticBoxSizer(wx.StaticBox(self, label="Books", size=sz), h)
        bks.Add(self.lst, 1, a, five)
        ts = wx.BoxSizer(wx.VERTICAL)
        bks.Add(ts)

        # seller sizer
        ss = wx.StaticBoxSizer(wx.StaticBox(self, label="Seller", size=sz), h)
        for id, name in Invoice.SELLER_CHOICES:
            rd = wx.RadioButton(self, label=name)
            rd.Bind(wx.EVT_RADIOBUTTON, self.OnRadio)
            ss.Add(rd, id, 0, a, 30)
            ss.Add((30, 30))
            if name == "Other":
                rd.SetValue(True)

        # info sizer
        infs = wx.StaticBoxSizer(wx.StaticBox(self, label="Info", size=sz), h)
        infs.Add(wx.StaticText(self, label="Total Price:"), 0, r | l | acv,
                 ten)
        infs.Add(self.total_price_lbl, 0, r | acv, 130)
        infs.Add(wx.StaticText(self, label="Date:"), 0, acv)
        infs.Add(self.date_txt, 0, a, five)

        bts = wx.BoxSizer(wx.HORIZONTAL)
        bts.Add(self.save_btn, 0, a, 1)
        bts.Add(self.cancel_btn, 0, a, 1)
        bts.Add(self.print_btn, 0, a, 1)

        ms.Add(bys, 0, a, ten)
        ms.Add(bks, 0, a, ten)
        ms.Add(infs, 0, a, ten)
        ms.Add(ss, 0, a, ten)
        ms.Add(bts, 0, a | wx.ALIGN_CENTER, ten)

        self.SetSizer(ms)
        self.SetInitialSize()

    def OnRadio(self, evt):
        rd = evt.GetEventObject()
        lbl = rd.GetLabel()
        for id, name in Invoice.SELLER_CHOICES:
            if name == lbl:
                self.seller = id


class AddBookDialog(wx.Dialog):
    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop("parent")
        wx.Dialog.__init__(self, *args, **kwargs)

        size = (150, -1)
        self.title_txt = wx.TextCtrl(self, size=size)
        self.no_txt = wx.lib.intctrl.IntCtrl(self, size=size)
        self.price_txt = wx.TextCtrl(self, size=size)
        self.serial_txt = wx.lib.intctrl.IntCtrl(self, size=size)
        size = (100, -1)
        self.ok_btn = wx.Button(self, wx.ID_OK, size=size)
        self.cancel_btn = wx.Button(self, wx.ID_CANCEL, size=size)
        self._bind()
        self._do_layout()

    def _bind(self):
        self.price_txt.Bind(wx.EVT_TEXT, self.OnPriceTextChange)
        self.ok_btn.Bind(wx.EVT_BUTTON, self.OnAddBtnClick)

    def _do_layout(self):
        lst = (("Title:", self.title_txt), ("No:", self.no_txt),
               ("Price:", self.price_txt), ("Serial:", self.serial_txt))
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        box = wx.StaticBoxSizer(wx.StaticBox(self, label="Book Information"),
                                wx.VERTICAL)
        for label, txt in lst:
            s = wx.BoxSizer(wx.HORIZONTAL)
            s.Add(wx.StaticText(self, label=label, size=(30, -1)), 0,
                  wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT, 10)
            s.Add(txt, 0, wx.ALL | wx.ALIGN_RIGHT, 10)
            # s.Add((-1, 5))
            box.Add(s)
        main_sizer.Add(box, 0, wx.ALL, 15)
        s = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(self.ok_btn, 0, wx.RIGHT | wx.BOTTOM, 10)
        s.Add(self.cancel_btn, 0, wx.LEFT | wx.BOTTOM, 10)
        main_sizer.Add(s, 0, wx.LEFT, 20)
        self.SetSizer(main_sizer)
        self.SetInitialSize()

    def OnPriceTextChange(self, event):
        if self.price_txt.GetValue() == "":
            return
        try:
            float(self.price_txt.GetValue())
        except ValueError:
            wx.MessageBox("Invalid value!", "Invalid Value")
            self.price_txt.Clear()

    def OnAddBtnClick(self, event):
        title = self.title_txt.GetValue()
        if not title:
            wx.MessageBox("Book must have a title.", "No Title!")
            return
        no = self.no_txt.GetValue()
        serial = self.serial_txt.GetValue()
        price = self.price_txt.GetValue()
        if Book.objects.filter(serial=serial).exists():
            wx.MessageBox("Duplicate serial", "Duplication!")
            self.Destroy()
            return
        book = Book(title=title, no=no, serial=serial, price=price)
        try:
            book.save()
        except Exception, e:
            wx.MessageBox(str(e))
        event.Skip()


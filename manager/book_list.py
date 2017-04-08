import sys
import wx
import wx.lib.mixins.listctrl  as  listmix
import wx.lib.intctrl
from wx.lib.mixins.listctrl import CheckListCtrlMixin
from manager.models import Book
from dialogs import InvoiceDialog, AddBookDialog
from django.forms.models import model_to_dict

_pk, _title,_no,_price,_serial=range(5)
columns = {
    _pk : "Id",
    _title: "Title",
    _no: "No",
    _price: "Price",
    _serial: "Serial",
}

class BookListCtrl(wx.ListCtrl,  CheckListCtrlMixin, listmix.TextEditMixin):
    def __init__(self, parent, ID, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0):
        self.parent = parent
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        CheckListCtrlMixin.__init__(self)
        listmix.TextEditMixin.__init__(self)
        # listmix.ListCtrlAutoWidthMixin.__init__(self)
        # self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)

    def OnCheckItem(self, index, flag):
        pk = self.GetItemData(index)

        if flag:
            what = "checked"
            no = self.GetItemText(index, _no)
            if int(no) > 0:
                self.parent.checked.append(pk)
            else:
                self.ToggleItem(index)
        else:
            what = "unchecked"
            if pk in self.parent.checked:
                self.parent.checked.remove(pk)
        if self.parent.checked:
            self.parent.invoice_btn.Enable()
        else:
            self.parent.invoice_btn.Disable()

        print self.parent.checked

    def SetStringItem(self, i, col, data):

        if not self.parent.list_populated:
            wx.ListCtrl.SetStringItem(self, i, col, data)
            pk = self.GetItemData(i)
            return

        pk = self.GetItemData(i)
        book = Book.objects.get(pk=pk)
        try:
            if col == _title:
                book.title = data
            elif col == _no:
                book.no = int(data)
            elif col == _price:
                book.price = float(data)
            elif col == _serial:
                book.serial = int(data)
            book.save()
        except ValueError:
            wx.MessageBox("Invalid value '%s' for column '%s'" %(data, columns[col]), "Invalid Value!")
            return

        wx.ListCtrl.SetStringItem(self, i, col, data)
        item = self.GetItem(i)
        if book.no == 0:
            item.SetTextColour(wx.RED)
        else:
            item.SetTextColour(wx.BLACK)
        self.SetItem(item)

class BookPanel(wx.Panel, listmix.ColumnSorterMixin):
    def __init__(self, parent, log):
        self.parent = parent
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)
        self.log = log
        self.lst = BookListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT |
                                                        wx.LC_SORT_ASCENDING|
                                                            wx.LC_VRULES|wx.LC_SINGLE_SEL)

        size = (55, -1)
        self.invoice_btn = wx.Button(self, label="Invoice", size=size)
        self.add_btn = wx.Button(self, label="Add", size=size)
        # self.edit_btn = wx.Button(self, label="Edit", size=size)
        self.del_btn = wx.Button(self, label="Delete", size=size)
        self.serial_txt = wx.lib.intctrl.IntCtrl(self)
        self.title_txt = wx.TextCtrl(self)

        self.checked = []
        self.query = Book.objects.all()

        self.itemDataMap = {b.pk:[str(b.pk).zfill(5), str(b.title), str(b.no),
                                  str(b.price), str(b.serial)] for b in self.query}
        listmix.ColumnSorterMixin.__init__(self, len(columns))
        self.SortListItems(_no, True)

        self._do_layout()
        self._bind()
        self._initial_attrs()

    def _initial_attrs(self):
        self.list_populated = False
        self.currentItem = 0
        self.lst.InsertColumn(_pk, columns[_pk])
        self.lst.InsertColumn(_title, columns[_title])
        self.lst.InsertColumn(_no, columns[_no], wx.LIST_FORMAT_RIGHT)
        self.lst.InsertColumn(_price, columns[_price], wx.LIST_FORMAT_RIGHT)
        self.lst.InsertColumn(_serial, columns[_serial], wx.LIST_FORMAT_RIGHT)
        self.lst.SetColumnWidth(_pk, 70)
        self.lst.SetColumnWidth(_title, 350)
        self.lst.SetColumnWidth(_no, 60)
        self.lst.SetColumnWidth(_price, 130)
        self.lst.SetColumnWidth(_serial, 200)
        self.lst.SetItemState(0, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
        self.populate_books_lst()
        self.invoice_btn.Disable()
        self.del_btn.Disable()

    def _bind(self):
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.lst)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected,
                  self.lst)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated, self.lst)
        # self.Bind(wx.EVT_LIST_DELETE_ITEM, self.OnItemDelete, self.lst)
        # self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick, self.lst)
        # self.Bind(wx.EVT_LIST_COL_RIGHT_CLICK, self.OnColRightClick, self.lst)
        # self.lst.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self.OnColBeginDrag)
        # self.Bind(wx.EVT_LIST_COL_DRAGGING, self.OnColDragging, self.lst)
        # self.Bind(wx.EVT_LIST_COL_END_DRAG, self.OnColEndDrag, self.lst)
        self.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.OnBeginEdit, self.lst)

        # self.lst.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
        # self.lst.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)

        self.serial_txt.Bind(wx.EVT_TEXT, self.OnSerialTextChange)
        self.title_txt.Bind(wx.EVT_TEXT, self.OnTitleTextChange)
        self.invoice_btn.Bind(wx.EVT_BUTTON, self.OnInvoiceClick)
        self.add_btn.Bind(wx.EVT_BUTTON, self.OnAddClick)
        self.del_btn.Bind(wx.EVT_BUTTON, self.OnDelClick)

        # for wxMSW
        # self.lst.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)

        # for wxGTK
        # self.lst.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)

    def populate_books_lst(self):
        self.list_populated = False
        self.lst.DeleteAllItems()

        for i, b in enumerate(self.query):
            self.lst.Append([str(b.pk).zfill(5), str(b.title), str(b.no),
                                  str(b.price), str(b.serial)])
            self.lst.SetItemData(i, b.pk)
            if self.lst.GetItemData(i) in self.checked:
                self.lst.CheckItem(i)
            if int(b.no) == 0:
                item = self.lst.GetItem(i)
                item.SetTextColour(wx.RED)
                self.lst.SetItem(item)

        self.list_populated = True

    def _do_layout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.lst, 1, wx.EXPAND)
        sizer.Add((-1, 10))
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(self.invoice_btn)
        btn_sizer.Add(self.add_btn, 0, wx.LEFT, 10)
        # btn_sizer.Add(self.edit_btn)
        btn_sizer.Add(self.del_btn)
        btn_sizer.Add(wx.StaticText(self, label="Name:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 5)
        btn_sizer.Add(self.title_txt)
        btn_sizer.Add(wx.StaticText(self, label="Serial:"),0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT| wx.RIGHT, 5)
        btn_sizer.Add(self.serial_txt)
        sizer.Add(btn_sizer)
        sizer.Add((-1, 5))

        if wx.Platform == "__WXMAC__" and hasattr(wx.GetApp().GetTopWindow(),
                                                  "LoadDemo"):
            self.useNative = wx.CheckBox(self, -1, "Use native listctrl")
            self.useNative.SetValue(not wx.SystemOptions.GetOptionInt(
                "mac.listctrl.always_use_generic"))
            self.Bind(wx.EVT_CHECKBOX, self.OnUseNative, self.useNative)
            sizer.Add(self.useNative, 0, wx.ALL | wx.ALIGN_RIGHT, 4)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)

    def OnDelClick(self, event):
        i = self.lst.GetFirstSelected()
        if i == -1:
            return
        pk = self.lst.GetItemData(i)
        b = Book.objects.get(pk=pk)
        b.delete()
        event.Skip()
        self.query = Book.objects.all()
        self.populate_books_lst()

    def OnAddClick(self, event):
        add_book_dlg = AddBookDialog(self, parent=self, title="Add New Book")
        if add_book_dlg.ShowModal() == wx.ID_OK:
            self.query = Book.objects.all()
            self.populate_books_lst()

    def OnInvoiceClick(self, event):
        invoice_dlg = InvoiceDialog(parent=self, title="New Invoice")
        invoice_dlg.ShowModal()
        self.parent.invoice_panel._populate()
        invoice_dlg.Destroy()

    def OnSerialTextChange(self, event):
        num = self.serial_txt.GetValue()
        if num == 0:
            self.query = Book.objects.all()
        else:
            self.query = Book.objects.filter(serial__startswith=num)
        self.populate_books_lst()

    def OnTitleTextChange(self, event):
        title = self.title_txt.GetValue()
        if title == "":
            self.query = Book.objects.all()
        else:
            self.query = Book.objects.filter(title__startswith=title)
        self.populate_books_lst()

    def OnUseNative(self, event):
        wx.SystemOptions.SetOptionInt("mac.listctrl.always_use_generic",
                                      not event.IsChecked())
        wx.GetApp().GetTopWindow().LoadDemo("ListCtrl")

    def GetListCtrl(self):
        return self.lst

    def OnRightDown(self, event):
        x = event.GetX()
        y = event.GetY()
        print "x, y = %s\n" % str((x, y))
        item, flags = self.lst.HitTest((x, y))

        if item != wx.NOT_FOUND and flags & wx.LIST_HITTEST_ONITEM:
            self.lst.Select(item)

        event.Skip()

    def getColumnText(self, index, col):
        item = self.lst.GetItem(index, col)
        return item.GetText()

    def OnItemSelected(self, event):
        ##print event.GetItem().GetTextColour()
        self.currentItem = event.m_itemIndex
        print "OnItemSelected: %s, %s, %s, %s\n" % (
        self.currentItem, self.lst.GetItemText(self.currentItem),
        self.getColumnText(self.currentItem, 1),
        self.getColumnText(self.currentItem, 2))

        if self.currentItem == 10:
            print "OnItemSelected: Veto'd selection\n"
            # event.Veto()  # doesn't work
            # this does
            self.lst.SetItemState(10, 0, wx.LIST_STATE_SELECTED)
        self.del_btn.Enable()
        event.Skip()

    def OnItemDeselected(self, evt):
        item = evt.GetItem()
        print "OnItemDeselected: %d" % evt.m_itemIndex

        # Show how to reselect something we don't want deselected
        # if evt.m_itemIndex == 11:
        #     wx.CallAfter(self.lst.SetItemState, 11, wx.LIST_STATE_SELECTED,
        #                  wx.LIST_STATE_SELECTED)

        self.del_btn.Disable()
        evt.Skip()

    def OnItemActivated(self, event):
        self.currentItem = event.m_itemIndex
        index = self.currentItem
        pk = self.lst.GetItemText(self.currentItem), self.lst.GetTopItem()
        pk = int(pk[0])
        print "OnItemActivated: %s TopItem: %s" % (index, pk)
        # no = self.lst.GetItemText(index, _no)
        # if int(no) > 0:
        self.lst.ToggleItem(index)
        # else:
        #     wx.MessageBox("No available book", "Not Available")
        # event.Skip()

    def OnBeginEdit(self, event):
        print "OnBeginEdit"
        if event.GetColumn() == 0:
            self.OnItemActivated(event)
            event.Veto()
        else:
            event.Allow()

    def OnItemDelete(self, event):
        print "OnItemDelete\n"

    def OnColClick(self, event):
        print "OnColClick: %d\n" % event.GetColumn()
        event.Skip()

    def OnColRightClick(self, event):
        event.Veto()
        item = self.lst.GetColumn(event.GetColumn())
        print "OnColRightClick: %d %s\n" % (event.GetColumn(), (
        item.GetText(), item.GetAlign(), item.GetWidth(), item.GetImage()))
        if self.lst.HasColumnOrderSupport():
            print "OnColRightClick: column order: %d\n" % \
                  self.lst.GetColumnOrder(
                event.GetColumn())

    def OnColBeginDrag(self, event):
        print "OnColBeginDrag\n"
        # event.Veto()
        ## Show how to not allow a column to be resized
        # if event.GetColumn() == 0:
        #    event.Veto()

    def OnColDragging(self, event):
        print "OnColDragging\n"

    def OnColEndDrag(self, event):
        print "OnColEndDrag\n"

    def OnDoubleClick(self, event):
        print "OnDoubleClick item %s\n" % self.lst.GetItemText(self.currentItem)

    def OnRightClick(self, event):
        print "OnRightClick %s\n" % self.lst.GetItemText(self.currentItem)

        # only do this part the first time so the events are only bound once
        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewId()
            self.popupID2 = wx.NewId()
            self.popupID3 = wx.NewId()
            self.popupID4 = wx.NewId()
            self.popupID5 = wx.NewId()
            self.popupID6 = wx.NewId()

            self.Bind(wx.EVT_MENU, self.OnPopupOne, id=self.popupID1)
            self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
            self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)
            self.Bind(wx.EVT_MENU, self.OnPopupFour, id=self.popupID4)
            self.Bind(wx.EVT_MENU, self.OnPopupFive, id=self.popupID5)
            self.Bind(wx.EVT_MENU, self.OnPopupSix, id=self.popupID6)

        # make a menu
        menu = wx.Menu()
        # add some items
        menu.Append(self.popupID1, "FindItem tests")
        menu.Append(self.popupID2, "Iterate Selected")
        menu.Append(self.popupID3, "ClearAll and repopulate")
        menu.Append(self.popupID4, "DeleteAllItems")
        menu.Append(self.popupID5, "GetItem")
        menu.Append(self.popupID6, "Edit")

        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.PopupMenu(menu)
        menu.Destroy()

    def OnPopupOne(self, event):
        print "Popup one\n"
        print "FindItem:", self.lst.FindItem(-1, "Roxette")
        print "FindItemData:", self.lst.FindItemData(-1, 11)

    def OnPopupTwo(self, event):
        print "Selected items:\n"
        index = self.lst.GetFirstSelected()

        while index != -1:
            print "      %s: %s\n" % (
            self.lst.GetItemText(index), self.getColumnText(index, 1))
            index = self.lst.GetNextSelected(index)

    def OnPopupThree(self, event):
        print "Popup three\n"
        self.lst.ClearAll()
        wx.CallAfter(self.populate_books_lst)

    def OnPopupFour(self, event):
        self.lst.DeleteAllItems()

    def OnPopupFive(self, event):
        item = self.lst.GetItem(self.currentItem)
        print item.m_text, item.m_itemId, self.lst.GetItemData(
            self.currentItem)

    def OnPopupSix(self, event):
        self.lst.EditLabel(self.currentItem)
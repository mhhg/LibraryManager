import sys
import wx
import wx.lib.mixins.listctrl  as  listmix
import wx.lib.intctrl
from wx.lib.mixins.listctrl import CheckListCtrlMixin
from manager.models import Book, Invoice
from dialogs import InvoiceDialog, AddBookDialog
from django.forms.models import model_to_dict
import wx.gizmos as gizmos
import images
#
# _pk, _title,_no,_price,_serial=range(5)
# columns = {
#     _pk : "Id",
#     _buyer: "Buyer",
#     _no: "No",
#     _price: "Price",
#     _serial: "Serial",
# }


class InvoicePanel(wx.Panel):
    def __init__(self, parent, log):
        self.log = log
        wx.Panel.__init__(self, parent, -1)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.tree = gizmos.TreeListCtrl(self, -1, style =
        wx.TR_DEFAULT_STYLE
        | wx.TR_HAS_BUTTONS
        #| wx.TR_TWIST_BUTTONS
        #| wx.TR_ROW_LINES
        | wx.TR_COLUMN_LINES
        #| wx.TR_NO_LINES
        | wx.TR_FULL_ROW_HIGHLIGHT
        )

        # create some columns
        self.tree.AddColumn("Books")
        self.tree.AddColumn("Buyer")
        self.tree.AddColumn("Seller")
        self.tree.AddColumn("Date")
        self.tree.AddColumn("No")
        self.tree.AddColumn("Price")
        self.tree.SetMainColumn(0) # the one with the tree in it...
        self.tree.SetColumnWidth(0, 200)
        self.tree.SetColumnWidth(1, 200)
        self.tree.SetColumnWidth(2, 100)
        self.tree.SetColumnWidth(3, 100)
        self.tree.SetColumnWidth(4, 50)

        self._populate()

        # self.tree.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate)

    def _populate(self):
        self.tree.DeleteAllItems()
        isz = (16,16)
        il = wx.ImageList(isz[0], isz[1])
        fldridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
        fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,   wx.ART_OTHER, isz))
        fileidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))
        smileidx    = il.Add(images.Smiles.GetBitmap())
        self.tree.SetImageList(il)
        self.il = il
        self.root = self.tree.AddRoot("All Invoices")
        self.tree.SetItemText(self.root, "", 1)
        self.tree.SetItemText(self.root, "", 2)
        self.tree.SetItemImage(self.root, fldridx, which = wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(self.root, fldropenidx, which = wx.TreeItemIcon_Expanded)


        for x, inv in enumerate(Invoice.objects.all()):
            txt = "ID: %d Books" % inv.pk
            buyer = inv.buyer_first_name + ' ' + inv.buyer_last_name
            seller = self.get_seller(inv)
            child = self.tree.AppendItem(self.root, txt)
            data = wx.TreeItemData()
            data.SetData(inv.pk)
            self.tree.SetItemData(child, data)
            total_no = inv.total_no()
            total_price = inv.total_price()
            date = inv.date
            self.tree.SetItemText(child, buyer , 1)
            self.tree.SetItemText(child, seller, 2)
            self.tree.SetItemText(child, str(date), 3)
            self.tree.SetItemText(child, str(total_no), 4)
            self.tree.SetItemText(child, str(total_price), 5)
            self.tree.SetItemImage(child, fldridx, which = wx.TreeItemIcon_Normal)
            self.tree.SetItemImage(child, fldropenidx, which = wx.TreeItemIcon_Expanded)

            for y, item in enumerate(inv.items.all()):
                txt = "%s" % item.book.title
                last = self.tree.AppendItem(child, txt)
                self.tree.SetItemText(last, buyer , 1)
                self.tree.SetItemText(last, seller, 2)
                self.tree.SetItemText(last, str(date), 3)
                self.tree.SetItemText(last, str(item.no), 4)
                self.tree.SetItemText(last, str(item.book.price), 5)
                self.tree.SetItemImage(last, fldridx, which = wx.TreeItemIcon_Normal)
                self.tree.SetItemImage(last, fldropenidx, which = wx.TreeItemIcon_Expanded)

        self.tree.Expand(self.root)

    def get_seller(self, inv):
        for id, name in Invoice.SELLER_CHOICES:
            if inv.seller == id:
                return name

    def OnActivate(self, evt):
        child = evt.GetItem()
        txt = self.tree.GetItemText(child)
        pk = self.tree.GetItemData(child).GetData()


    def OnRightUp(self, evt):
        pos = evt.GetPosition()
        item, flags, col = self.tree.HitTest(pos)
        if item:
            self.log.write('Flags: %s, Col:%s, Text: %s' %
                           (flags, col, self.tree.GetItemText(item, col)))

    def OnSize(self, evt):
        self.tree.SetSize(self.GetSize())
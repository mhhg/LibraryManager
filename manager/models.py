from django.db import models

# class Publisher(models.Model):
# name = models.CharField(max_length=30)
# address = models.CharField(max_length=50)
#     city = models.CharField(max_length=60)
#     state_province = models.CharField(max_length=30)
#     country = models.CharField(max_length=50)
#     website = models.URLField()
#
#     def __unicode__(self):
#         return self.name
#
#
# class Author(models.Model):
#     first_name = models.CharField(max_length=30)
#     last_name = models.CharField(max_length=40)
#     email = models.EmailField()
#
#     def __unicode__(self):
#         return u'%s %s' % (self.first_name, self.last_name)

# class Person(Author):
#     pass


class Book(models.Model):
    title = models.CharField(max_length=100)
    # authors = models.ManyToManyField(Author, blank=True)
    serial = models.BigIntegerField(unique=True)
    no = models.PositiveSmallIntegerField(default=1)
    price = models.FloatField(null=False)
    # publisher = models.ForeignKey(Publisher, null=True, blank=True)
    # publication_date = models.DateField(null=True, blank=True)
    # added_on = models.DateTimeField(auto_now_add=True)
    # num_pages = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.title


class InvoiceItem(models.Model):
    book = models.ForeignKey(Book)
    invoice = models.ForeignKey('Invoice', related_name='items',
                                related_query_name='invoices')
    no = models.PositiveSmallIntegerField(default=1)

    def __unicode__(self):
        return self.book.title


class Invoice(models.Model):
    books = models.ManyToManyField(Book, through=InvoiceItem)
    buyer_first_name = models.CharField(max_length=100)
    buyer_last_name = models.CharField(max_length=100)
    KASHANI = 1
    HOJABRI = 2
    OTHER = 3
    SELLER_CHOICES = (
        (KASHANI, "Kashani"),
        (HOJABRI, "Hojabri"),
        (OTHER, "Other"),
    )
    seller = models.PositiveSmallIntegerField(choices=SELLER_CHOICES,
                                              default=OTHER)
    date = models.DateTimeField()

    def __unicode__(self):
        return self.buyer_first_name

    def total_no(self):
        n = 0
        for item in self.items.all():
            n += item.no
        return n

    def total_price(self):
        t = 0
        for item in self.items.all():
            t += item.book.price
        return t


from django.dispatch import receiver
from django.db.models.signals import *

@receiver(post_save, sender=InvoiceItem)
def subtract_sold_books_no(sender, instance, **kwargs):
    instance.book.no -= instance.no
    instance.book.save()
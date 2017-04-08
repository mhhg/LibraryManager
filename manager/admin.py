from django.contrib import admin
from manager.models import *


admin.site.register(Book)
# admin.site.register(Person)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
# admin.site.register(Author)
# admin.site.register(Publisher)
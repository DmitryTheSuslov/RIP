from django.contrib import admin
from .models import *

admin.site.register(Address)
admin.site.register(Fixation)
admin.site.register(AddressFixation)
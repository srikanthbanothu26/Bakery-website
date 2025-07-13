from django.contrib import admin
from .models import Bakery, UnitOfMeasurements, UserInfo, Address, Countries, State


class BakeryAdmin(admin.ModelAdmin):
    list_display = ('name', 'active')


admin.site.register(Bakery, BakeryAdmin)
admin.site.register(UnitOfMeasurements)
admin.site.register(UserInfo)
admin.site.register(Address)
admin.site.register(Countries)
admin.site.register(State)

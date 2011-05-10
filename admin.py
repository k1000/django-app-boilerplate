# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from models import BedsonlineDestinatios, BedsonlineHotelBooking
class BedsonlineDestinatiosAdmin(admin.ModelAdmin):

    order_by = ("country_name")
    search_fields = ("destination_name", "destination_code"  )
    list_filter = ( "country_name", )

class HotelBookingAdmin(admin.ModelAdmin):
    queryset = BedsonlineHotelBooking.objects.booked()
    fieldsets = (
        (None, {
                'fields': ( ('offer',"provider",),
                            ( "booking",),
                            ("nr_adults", "nr_kids", ),
                            ("start", "end"),
                            ("nr_rooms"),
                            ("price", "defferd_payment", "comission", ),
                            "organize_fly",
                            "description",
                            "client_comments",
                          )
        }),
    )
        
admin.site.register(BedsonlineDestinatios, BedsonlineDestinatiosAdmin )
admin.site.register(BedsonlineHotelBooking )
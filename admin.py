# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class XXXAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {
                'fields': ( )
        }),
    )
    list_display = ( )
    date_hierarchy = ''
    prepopulated_fields = {'slug':('title',)}
    search_fields = (  )
    list_filter = ( )
    exclude = (   )
    
admin.site.register(XXX, XXXAdmin )

# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from views.booking import BedsonlineHotelBookingView
urlpatterns = patterns('',
    url(r'^destination_field$', 'bedsonline.views.offer.get_detination_field', 
                name='bedsonline_destination_field'),
    #url(r'^(?P<object_id>[0-9]+)/(?P<name>[\w-]*)/$', 'bedsonline.views.offer.get_hotel', 
    #            name='bedsonline_hotel'),
    url(r'^(?P<object_id>[0-9]+)/(?P<shrui>[\w-]*)/$', BedsonlineHotelBookingView.as_view(), 
                            name='bedsonline_hotel'),
    #url(r'^(?P<object_id>[0-9]+)/(?P<name>[\w-]*)/$', BedsonlineHotelBookingView.as_view(), 
                                                   # name='bedsonline_hotel_info'),
    url(r'^$', 'bedsonline.views.offer.destiantions_search', 
                name='bedsonline_destination_search'),
)

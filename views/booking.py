# -*- coding: utf-8 -*-
# Create your views here.
import urllib

from reservation.views.base_booking import BaseBookingView
from bedsonline.models import BedsonlineHotelBooking
from bedsonline.forms import BedsonlineHotelBookingForm
from bedsonline.views.offer import get_booking_object, get_hotel_data, get_session_id, get_offer_data

from bedsonline.templatetags.transdata import strtotime

class BedsonlineHotelBookingView(BaseBookingView):
    success_url = "/reserva/checkout/"
    template_name = "bedsonline/hotel.html"
    form_class = BedsonlineHotelBookingForm
    query_str = BedsonlineHotelBooking.objects.all()
    xml_respond = None
    object_id = None
    
    def get_offer(self, offer_id, shrui ):
        query_str = urllib.urlencode( self.request.GET )
        self.xml_respond = self.request.session.get( query_str, None)
        if self.xml_respond:
            return get_booking_object(self.xml_respond, offer_id, shrui )
        else:
            return None
        
    def get_initial(self, *args, **kwargs):
        hotel_id = self.kwargs["object_id"]
        shrui = self.kwargs["shrui"]
        data = dict(
            client = self._get_or_cerate_user( ),
            hotel_id = hotel_id,
        )
        offer = self.get_offer(hotel_id, shrui)
        if offer:
            data.update(offer)
            data["booking_data" ] = offer
            data["client_token" ] = get_session_id( self.request )
            data["kids_ages"] = self.request.GET.get("kids_ages")
            data["offer" ] = data["booking_data"].get("shrui")
            data["query" ] = urllib.urlencode( self.request.GET )
        return data
        
    def get_context_data(self,*args, **kwargs):
        context = super(BedsonlineHotelBookingView, self).get_context_data(*args, **kwargs)
        hotel_id = context["hotel_id"]
        
        #if self.request.GET.has_key("page"):
        #    context['booking_data'] = get_booking_data(self.xml_respond, hotel_id )
        if "" in self.request.session:
            context["checkout"] = True
        hotel_data = get_hotel_data( hotel_id ) 
        context.update(hotel_data )
        return context
    
    def form_valid(self, form):
        booking = form.save(commit=False)
        data = self.get_initial()
        booking.set_data( data )
        booking.save()
        self.push_to_session(booking.id)
        self.remember_dates(booking.start)
        return super(BaseBookingView, self).form_valid(form)
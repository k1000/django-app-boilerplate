# -*- coding: utf-8 -*-
import os
import urllib
import simplejson
import logging
from lxml import objectify

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.forms.formsets import formset_factory
from django.conf import settings
from django.template.defaultfilters import slugify

from bedsonline.forms import DestinationSearchForm, AddKidForm
from bedsonline.models import BedsonlineDestinatios
from bedsonline.api import get_destinations, get_errors

from bedsonline.templatetags.transdata import strtotime

logger = logging.getLogger(__name__)

SHOW_DIRECT_PAYMENT = True
SHOW_NET_PRICE = True
KIDS_AGE_RANGE = range(0, 15)

def get_offer_data( offer_object ):
    category = offer_object.HotelInfo.Category.get("shortname")[:1],
    try:
        cat = range(int(category[0]) )
    except ValueError:
        cat = []
    out = dict(
        hotel_name = offer_object.HotelInfo.Name,
        hotel_id = offer_object.HotelInfo.Code,
        availability_token = offer_object.get("availToken"),
        contract_name = offer_object.ContractList.Contract.Name,
        incoming_office = offer_object.ContractList.Contract.IncomingOffice.get("code"),
        destination_name = offer_object.HotelInfo.Destination.Name,
        destination_type = offer_object.HotelInfo.Destination.get("type"),
        destination_code = offer_object.HotelInfo.Destination.get("code"),
        destination_zone = offer_object.HotelInfo.Destination.ZoneList.Zone,
        customer_type = "AD", #TODO! chweck this out
        start = strtotime( offer_object.DateFrom.get("date"), "%Y%m%d"),
        end = strtotime( offer_object.DateTo.get("date"), "%Y%m%d"),
        offers = [],
        images = [i.Url for i in offer_object.HotelInfo.ImageList.getchildren() ],
        category = cat,
        category_type = offer_object.HotelInfo.Category[2:],
        lat = offer_object.HotelInfo.Position.get("latitude"),
        lng = offer_object.HotelInfo.Position.get("longitude"),
    )
    for room in offer_object.getchildren()[5:]:
        print room
        offer_data = dict(
            shrui = room.HotelRoom.get("SHRUI"),
            board = room.HotelRoom.Board,
            board_type = room.HotelRoom.Board.get("type"),
            board_code = room.HotelRoom.Board.get("code"),
            room = room.HotelRoom.RoomType,
            room_type = room.HotelRoom.RoomType.get("type"),
            room_code = room.HotelRoom.RoomType.get("code"),
            room_characteristic = room.HotelRoom.RoomType.get("characteristic"),
            nr_adults = room.HotelOccupancy.Occupancy.AdultCount,
            nr_kids = room.HotelOccupancy.Occupancy.ChildCount,
            nr_rooms = room.HotelOccupancy.RoomCount,
            price = str(room.HotelRoom.Price.Amount),
        )
        out["offers"].append(offer_data)
    return out
    
def parse_destination_respond(xml):
    """docstring for gwt_destination_data"""
    if xml is None:
        pass
    data = objectify.fromstring( xml )
    error_list = getattr(data, "ErrorList", None)
    if error_list:
        return get_errors( error_list, xml )
    else:
        return dict(
            nr_items = data.values()[2],
            expiration = data.values()[1],
            echo_token = data.values()[3],
            nr_pages = range(1, int(data.PaginationData.items()[1][1])+1 ),
            current_page = int(data.PaginationData.items()[0][1]),
            destinations = [ get_offer_data(s) for s in data.getchildren()[2:]],
        )

def get_session_id(request):
    return request.session.session_key[:24]
    
def destiantions_search(request):
    """docstring for get_destiantions"""
    data = {}
    form_kwargs = {}
    country = request.GET.get("country", None)
    data["kids_age_range"] = KIDS_AGE_RANGE
    if country:
        form_kwargs['country_code'] = country
    if request.method == "POST" or "page" in request.GET:
        AddKidFormSet = formset_factory(AddKidForm)
        form = DestinationSearchForm(request.REQUEST, form_kwargs)
        kids_ages = [ int(age) for age in request.REQUEST.getlist("kids_ages") if age ] 
        data["kids_ages"] = kids_ages
        if form.is_valid():
            session_query = urllib.urlencode( request.REQUEST )
            if request.session.has_key(session_query) and request.session[session_query] != "":
                xml_respond = request.session[session_query]
            else:
                request_query = form.cleaned_data
                request_query["page"]= request.REQUEST.get("page",1)
                if SHOW_DIRECT_PAYMENT:
                    request_query["show_direct_payment"] = "Y"
                if SHOW_NET_PRICE:
                    request_query["show_net_price"] = "Y"
                request_query["sessionId"] = get_session_id(request)
                request_query["kids_ages"] = kids_ages
                request_query["nr_kids"] = len(kids_ages)
                xml_request, xml_respond = get_destinations( request_query )
                #update session
                request.session[session_query] = xml_respond
                request.session["last_query"] = session_query
            
            bedsonline_data = parse_destination_respond( xml_respond )
            if "errors" in bedsonline_data:
                data["error"] = u"""Se han registrado errores en el sistema de reserva. 
                Por favor vuelve más tarde. """
            else:
                data.update(bedsonline_data)

            q = request.REQUEST.copy()
            data["paged_query_string"] = urllib.urlencode(q)
            #eliminate page from query
            query = dict( [(k, q[k] )for k in q if k != "page" ] )
            data["query_string"] = urllib.urlencode(query)
    else:
        form = DestinationSearchForm()

    data["search_form"] = form
    return render_to_response("bedsonline/search_destinations_list.html", 
                    data,
                    context_instance=RequestContext(request))
    
def get_detination_field(request):
    country_code = request.GET.get("country_code", None)
    destiantions = BedsonlineDestinatios.objects.get_destination_in( country_code )
    html = simplejson.dumps(destiantions)
    return HttpResponse(html)

def get_booking_object(xml_respond, hotel_id, shrui):
    """get booking data for given hotel_id and shrui in xml_respond"""
    respond_data = parse_destination_respond(xml_respond)
    destinations_data = respond_data.get("destinations")
    for hotel in destinations_data:
        if int(hotel.get("hotel_id") ) == int(hotel_id):
            for offer in hotel.get("offers"):
                if str(shrui) == slugify(offer.get("shrui") ):
                    del(hotel["offers"])
                    offer.update(hotel)
                    return offer
    return None

def get_hotel_data(object_id):
    data = {}
    lang = "ESP"
    filename = "%s.xml" % object_id
    file_path = str(os.path.join(settings.PROJECT_PATH, 'bedsonline/resources', lang, filename) )
    try:
        xml_hotel_data = open(file_path, 'r')
        response_data = objectify.parse(xml_hotel_data)
        hotel_data = response_data.getroot()    
        data = dict(
            hotel_id = object_id,
            hotel_data = hotel_data,
        )
    except:
        data = {}
    return data
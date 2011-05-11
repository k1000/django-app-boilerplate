# -*- coding: utf-8 -*-
import datetime
from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from utils.forms.form_honeypot import FormHoneypotMixin

from models import BedsonlineDestinatios, BedsonlineHotelBooking

class DestinationFieldForm(forms.Form):
    destination = forms.ChoiceField(label=_(u"destino"), choices= [] )
    def __init__(self, country_code=None, *args, **kwargs):
        super(DestinationFieldForm,self).__init__(*args, **kwargs)
        if country_code:
            destiantions = BedsonlineDestinatios.objects.get_destination_in( country_code )
            self.fields['destination'].choices = destiantions

class AddKidForm(forms.Form):
    kid_age = forms.ChoiceField(label=_(u"edad del niño"), 
                    choices=[(e,e) for e in range(0,14)] )

class DestinationSearchForm(forms.Form):
    REGIMES = (
        (1, _(u"pensión")),
        (2, _(u"media pensión")),
        (3, _(u"todo incluido")),
        (3, _(u"todo asdasda incluido")),
    )
    country = forms.ChoiceField(label=_(u"país"),
                choices=BedsonlineDestinatios.objects.get_countrys() )
    destination = forms.ChoiceField(label=_(u"destino"), choices= [] )
    check_in = forms.DateField(label=_(u"comienzo"), required=True)
    check_out = forms.DateField(label=_(u"fin"), required=True)
    nr_adults = forms.ChoiceField(label=_(u"nr adultos"), 
                choices=[(e,e) for e in range(1,7)] )
    #regime = forms.ChoiceField(label=_(u'régimen'), choices= REGIMES, required=False)
    
    def __init__(self, *args, **kwargs):
        super(DestinationSearchForm,self).__init__(*args, **kwargs)
        if args:
            code = args[0].get("country", None)
        else:
            code = kwargs.get("country_code", None)
        
        if code:
            destiantions = BedsonlineDestinatios.objects.get_destination_in( code )
            self.fields['destination'].choices = destiantions
    
    def clean_check_in(self):
        date = self.cleaned_data["check_in"] + datetime.timedelta(days=1) 
        if date  < datetime.date.today():
            raise forms.ValidationError(_("La fecha tiene que ser posterior de hoy"))
        return date
        
    def clean_check_out(self):
        date = self.cleaned_data["check_out"] + datetime.timedelta(days=1) 
        if date < datetime.date.today():
            raise forms.ValidationError(_("La fecha tiene que ser posterior de hoy"))
        return date
        
    def clean(self):
        data = self.cleaned_data
        check_in = data.get("check_in")
        check_out = data.get("check_out")
        if check_in and check_out:
            if check_in > check_out:
                raise forms.ValidationError(_(u"La fecha no salida no pudede ser anterior a la vuelta"))
            if check_out - check_in > datetime.timedelta(days=31):
                raise forms.ValidationError(_(u"La duración de la estancia no puede sewr superior a 31 días"))
        return data
            

class BedsonlineHotelBookingForm( FormHoneypotMixin, ModelForm):
    class Meta:
        model = BedsonlineHotelBooking
        fields = ( "offer", "organize_fly", "query", "client_comments", "client_token", "hotel_id")

        widgets = { 
            "offer": forms.HiddenInput(),
            "client_token": forms.HiddenInput(),
            "hotel_id": forms.HiddenInput(),
            "query": forms.HiddenInput(),
        }

    def save(self, force_insert=False, force_update=False, commit=True):
        booking = super(BedsonlineHotelBookingForm, self).save(commit=False)
        booking.booking_id = 0
        if commit:
            booking.save()
        return booking

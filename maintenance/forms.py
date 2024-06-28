from django.core.exceptions import ValidationError
from django.core import validators
from django import forms
from organization.models import Owner, User, Application, Area, Container, Scope


class SampleForm(forms.Form):
    title = forms.CharField(
        validators=[validators.MinLengthValidator(5)]
    )
    zahl = forms.IntegerField(
        validators=[validators.MaxValueValidator(
            100), validators.MinValueValidator(7)]
    )
    datum = forms.DateField(required=False, widget=forms.DateInput)


class ScopeForm(forms.ModelForm):
    class Meta:
        model = Scope
        fields = ['application',  'business_unit_1', 'business_unit_2', 'business_unit_3','business_unit_4','business_unit_5', 'desc', 'type', ]
        
    def __init__(self, application, **kwargs):
        super().__init__(**kwargs)
        self.fields['application'].widget = forms.HiddenInput()
        if application.business_unit_1:
            self.fields['business_unit_1'].label = application.business_unit_1
            self.fields['business_unit_1'].help_text = application.regex_1
        else:
            self.fields['business_unit_1'].widget = forms.HiddenInput()
        if application.business_unit_2:
            self.fields['business_unit_2'].label = application.business_unit_2
            self.fields['business_unit_2'].help_text = application.regex_2
        else:
            self.fields['business_unit_2'].widget = forms.HiddenInput()
        if application.business_unit_3:
            self.fields['business_unit_3'].label = application.business_unit_3
            self.fields['business_unit_3'].help_text = application.regex_3
        else:
            self.fields['business_unit_3'].widget = forms.HiddenInput()
        if application.business_unit_4:
            self.fields['business_unit_4'].label = application.business_unit_4
            self.fields['business_unit_4'].help_text = application.regex_4
        else:
            self.fields['business_unit_4'].widget = forms.HiddenInput()
        if application.business_unit_5:
            self.fields['business_unit_5'].label = application.business_unit_5
            self.fields['business_unit_5'].help_text = application.regex_5
        else:
            self.fields['business_unit_5'].widget = forms.HiddenInput()
            

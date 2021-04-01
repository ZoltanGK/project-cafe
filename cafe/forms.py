from django import forms
from cafe.models import Contact

class ContactForm(forms.ModelForm):
    name = forms.CharField(max_length=64, required=False, label="Name (optional)")
    date = forms.DateField(label = "Date")
    issue = forms.CharField(label = "Submit Issue", max_length = 1024, widget=forms.Textarea)

    class Meta:
        model = Contact
        fields = ('name','date', 'issue')
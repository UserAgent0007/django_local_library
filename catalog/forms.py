from django import forms

import datetime

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _ # Необхідне для здійснення перекладу потім


from django.forms import ModelForm

from catalog.models import BookInstance, Book, Author, Genre

# class RenewBookModelForm(ModelForm):
#     def clean_due_back(self):
#        data = self.cleaned_data['due_back']

#        # Check if a date is not in the past.
#        if data < datetime.date.today():
#            raise ValidationError(_('Invalid date - renewal in past'))

#        # Check if a date is in the allowed range (+4 weeks from today).
#        if data > datetime.date.today() + datetime.timedelta(weeks=4):
#            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

#        # Remember to always return the cleaned data.
#        return data

#     class Meta:
#         model = BookInstance
#         fields = ['due_back']
#         labels = {'due_back': _('Renewal date')}
#         help_texts = {'due_back': _('Enter a date between now and 4 weeks (default 3).')}

class BookAdd (forms.Form):

    title = forms.CharField (max_length=200, required=True)
    author = forms.ModelChoiceField (queryset=Author.objects.all(), required=True)
    summary = forms.CharField (widget=forms.Textarea, max_length=1000, help_text='Enter a brief description of the book', required=True)
    isbn = forms.CharField (max_length=200, label='ISBN', required=True)
    genre = forms.ModelMultipleChoiceField (queryset=Genre.objects.all(), help_text='Select a genre for this book', required=True)

    def clean_isbn (self):

        isbn_entered = self.cleaned_data['isbn']

        if Book.objects.filter(isbn=isbn_entered).exists():

            raise ValidationError(_('you entered non unique isbn for a book'))
        
        
        return isbn_entered

class BookUpdate (ModelForm):

    def clean_isbn (self):

        isbn = self.cleaned_data['isbn']

        if Book.objects.filter(isbn=isbn).exclude(pk=self.instance.pk).exists():

            raise ValidationError (_('Non unique isbn'))
        
        else:

            return isbn
        
    class Meta:

        model = Book
        fields = '__all__'
        

class RenewBookForm (forms.Form):

    renewal_date = forms.DateField (help_text="Enter a date between now and 4 weeks (default 3).")

    def clean_renewal_date (self):

        data = self.cleaned_data['renewal_date']

        if data < datetime.date.today():

            raise ValidationError (_('Invalid date - renewal in past'))
        
        elif data > datetime.date.today() + datetime.timedelta(weeks=4):

            raise ValidationError (_('Invalid date - renewal more than 4 weeks ahead'))
        
        return data


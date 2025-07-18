from django.db import models
from django.urls import reverse
from django.conf import settings
import uuid
from datetime import date

# Create your models here.

class Genre (models.Model):
    """Represents genre of the book"""

    name = models.CharField (max_length=200, help_text="Enter a book genre (e.g. Science Fiction)")

    def __str__ (self):
        """represents model object"""
        
        
        return self.name
    
class Book (models.Model):

    """represents general info about book, but not a single copy"""

    title = models.CharField (max_length = 200)

    author = models.ForeignKey ('Author', on_delete=models.SET_NULL, null=True) # Брати все в лапки і не вимахуватися !!! ('Author')
    summary = models.TextField (max_length=1000, help_text='Enter a brief description of the book')
    isbn = models.CharField ('ISBN', max_length=200, unique=True)
    genre = models.ManyToManyField(Genre, help_text='Select a genre for this book') #  

    class Meta:

        ordering = ['title']

    def __str__ (self):

        return self.title
    
    def get_absolute_url(self): 
        """Returns the URL to access a detail record for this book.""" 

        return reverse('book-detail', args=[str(self.id)]) 
    
    def display_genre (self):

        return ', '.join (genre.name for genre in self.genre.all()[:3])
    
    display_genre.short_description = 'Genre'

class BookInstance (models.Model):
    """model represents a specific copy"""

    id = models.UUIDField (primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular book across whole library')
    book = models.ForeignKey ('Book', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField (max_length=200)
    #blank = true - дозволяє порожні рядки
    due_back = models.DateField (null=True, blank=True)

    borrower = models.ForeignKey (settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    # список для вибору

    LOAN_STATUS = ( 
        ('m', 'Maintenance'), 
        ('o', 'On loan'), 
        ('a', 'Available'), 
        ('r', 'Reserved'), 
    )

    status = models.CharField (
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text='book awailability'
    ) 

    class Meta:

        ordering=['due_back']

        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__ (self):

        return f'{self.id} ({self.book.title})'

    @property
    def is_overdue (self):

        return bool(self.due_back and date.today() > self.due_back) 

class Author (models.Model):

    first_name = models.CharField (max_length=100)
    last_name = models.CharField (max_length=100)
    date_of_birth = models.DateField(null=True, blank=True) 
    date_of_death = models.DateField('died', null=True, blank=True) 

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url (self):

        return reverse ('author-detail', args=[str(self.id)])
    
    def __str__ (self):

        return f'{self.last_name}, {self.first_name}'


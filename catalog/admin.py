from django.contrib import admin

# Register your models here.

from .models import Author, Genre, Book, BookInstance


class BookInstanceInline (admin.TabularInline):

    model = BookInstance
    extra = 0 # не показує додаткові поля для введення

class BookInline (admin.StackedInline):

    model = Book
    extra = 0

class AuthorAdmin (admin.ModelAdmin):

    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]

    inlines = [BookInline]

@admin.register(Book)
class BookAdmin (admin.ModelAdmin):

    list_display = ('title', 'author', 'display_genre') # display_genre - функція яка буде визначена нами нижче

    inlines = [BookInstanceInline]


@admin.register (BookInstance)
class BookInstanceAdmin (admin.ModelAdmin):

    list_filter = ['status' ,'due_back']
    list_display = ['book', 'status', 'borrower', 'due_back', 'id']
    # exclude = ['id'] те що ми не хочемо бачити на екрані

    # Здійснимо групування fieldsets

    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),

        ('Availability', {
            'fields': ('status', 'borrower', 'due_back')
        })
    )

# admin.site.register (Author)
admin.site.register (Genre)
# admin.site.register (Book)
# admin.site.register (BookInstance)
admin.site.register (Author, AuthorAdmin)


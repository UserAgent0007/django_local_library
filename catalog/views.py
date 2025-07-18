from django.shortcuts import render, get_object_or_404 # заповнює скелет HTML файлу динамічно і повертає назад готову відповідь у браузер

from .models import Book, BookInstance, Author, Genre

from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from .forms import RenewBookForm, BookAdd, BookUpdate
import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import CreateView, UpdateView, DeleteView

from django.db.models import Q
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


# Create your views here.

def index (request):

    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    num_authors = Author.objects.count() # мається наувазі, що all застосовано за замовчуванням

    num_genrs = Genre.objects.all().count()

    num_visits = request.session.get ('num_visits', 0) # Якщо нема такого ключа, то він буде встановлений автоматично і отримає, вказане початкове значення (0)
    num_visits += 1
    request.session['num_visits'] = num_visits

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genrs': num_genrs,
        'num_visits': num_visits
    }

    return render(request, 'index.html', context=context)


def search_book_by_name (request):

    req = request.GET.get('q')
    books = []

    if req:

        books = Book.objects.filter (

            Q(title__icontains = req)

        ).distinct()

    context = {

        'req': req,
        'books': books
    }

    return render(request, 'search.html', context = context)

class BookListView (generic.ListView):

    model = Book
    paginate_by = 2

    # modifications

    context_object_name = 'book_list'

    # You can change parameters of making select

    # queryset = Book.objects.filter(title__icontains='war')[:5] 

    template_name = 'templates/catalog/book_list.html'


# examlple of checking if book exists
#
# def book_detail_view(request, primary_key): 
#     try: 
#         book = Book.objects.get(pk=primary_key) 
#     except Book.DoesNotExist: 
#         raise Http404('Book does not exist') 
#     return render(request, 'catalog/book_detail.html', context={'book': book}) 

class BookDetailView (generic.DetailView):

    model = Book

    def get_context_object_name(self, obj):

        return 'book_details'

class AuthorListView (generic.ListView):

    model = Author
    paginate_by = 2

    def get_context_object_name(self, obj):

        return 'author_list'
    
class AuthorDetailView (generic.DetailView):

    model = Author
    
    def get_context_object_name(self, obj):

        return 'author_info'
    
class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):

        return (
            BookInstance.objects.filter(

                Q(borrower=self.request.user),
                Q(status__exact='o')

            )
            .order_by('due_back')
        )
    
class LoanedAllBooksListView (PermissionRequiredMixin, generic.ListView):

    model = BookInstance
    template_name = 'catalog/all_books.html'
    paginate_by = 10

    permission_required = 'catalog.can_mark_returned'

    def get_queryset(self):

        return (
            BookInstance.objects.filter(status__exact='o').order_by('due_back')
        )
    
    def get_context_object_name(self, obj):

        return 'all_books'
    
@login_required
@permission_required ('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian (request, pk):

    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':

        form = RenewBookForm(request.POST) # прив’язка форми до даних. request.POST - словник, який містить все відправлене на сервер

        if form.is_valid():

            book_instance.due_back = form.cleaned_data['renewal_date']

            book_instance.save()

            return HttpResponseRedirect (reverse('all-borrowed'))
        
    else:

        proposed_renewal_date = datetime.date.today()

        form = RenewBookForm (initial={'renewal_date':proposed_renewal_date})

    context={
        'form': form,
        'book_instance': book_instance
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

@login_required
@permission_required (perm='catalog.add_book', raise_exception=True)
def add_book (request):

    success_url = reverse_lazy ('books')
    
    if request.method == 'GET':

        form = BookAdd()

    elif request.method == 'POST':

        form = BookAdd(request.POST)

        if form.is_valid():

            data_list = form.cleaned_data

            new_book = Book (
                title = data_list['title'],
                author = data_list['author'],
                summary = data_list['summary'],
                isbn = data_list['isbn']
            )

            new_book.save()
            new_book.genre.set(data_list['genre'])

            return HttpResponseRedirect (success_url)
    
    context = {
        'form':form
    }

    return render (request, 'catalog/add_book.html', context=context)

@login_required
@permission_required (perm='catalog.change_author', raise_exception=True)
def update_book (request, pk):

    success_url = reverse_lazy ('books')
    book = get_object_or_404 (Book, pk=pk)

    if request.method == 'GET':

        form = BookUpdate(instance=book)
    
    elif request.method == 'POST':

        form = BookUpdate (request.POST, instance=book)

        if form.is_valid():

            form.save()
            
            return HttpResponseRedirect (success_url)

    context = {
        'form':form,
        'book': book
    }

    return render (request, 'catalog/update_book.html', context = context)

class DeleteBook (PermissionRequiredMixin, DeleteView):

    model = Book
    success_url = reverse_lazy ('books')
    permission_required = 'catalog.book_delete'

    def form_valid (self, form):

        try:
            self.object.delete()
            return HttpResponseRedirect (self.success_url)
        
        except Exception as e:

            return HttpResponseRedirect (reverse('delete-book', kwargs={'pk':self.object.pk}))


class AuthorCreate (PermissionRequiredMixin, CreateView):

    model = Author
    permission_required = 'catalog.add_author'

    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

    initial = {'date_of_death': '11/11/2023'}

class AuthorChange (PermissionRequiredMixin, UpdateView):

    model = Author
    permission_required = 'catalok.change_author'
    fields = '__all__'

class AuthorDelete (PermissionRequiredMixin, DeleteView):

    model = Author
    success_url = reverse_lazy ('author-list')
    permission_required = 'catalog.delete_author'

    def form_valid (self, form): # Викликається, коли форма була успішно провалідована

        try:

            self.object.delete()
            return HttpResponseRedirect (self.success_url)
        
        except Exception as e:

            return HttpResponseRedirect (reverse("author-delete", kwargs={"pk": self.object.pk}))
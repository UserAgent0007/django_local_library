from . import views
from django.urls import path, re_path


urlpatterns = [ 
    path('', views.index, name='index'),
    path('search/', views.search_book_by_name, name='search'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('books/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),

    re_path(r'authors/', views.AuthorListView.as_view(), name='author-list'),
    # re_path(r'author/(?P<author_id>[/d]+)', views.AuthorDetailView.as_view(), name='author-detail')
    path ('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail')
]

urlpatterns += [
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    path ('loaned_books/', views.LoanedAllBooksListView.as_view(), name="all-borrowed")
]

urlpatterns += [
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
]

urlpatterns += [
    path('author/<int:pk>/update', views.AuthorChange.as_view(), name='author-update'),
    path('author/create', views.AuthorCreate.as_view(), name='author-create'),
    path('author/<int:pk>/delete', views.AuthorDelete.as_view(), name='author-delete')
]

urlpatterns += [
    path ('book/add_new', views.add_book, name='new-book'),
    path('book/<int:pk>/update', views.update_book, name='update-book'),
    path('book/<int:pk>/delete', views.DeleteBook.as_view(), name='delete-book')
]

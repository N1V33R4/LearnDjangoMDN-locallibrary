from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Book, BookInstance, Author, Genre


def index(request):
  """View function for home page of site."""

  num_books = Book.objects.all().count()
  num_instances = BookInstance.objects.all().count()
  num_instances_available = BookInstance.objects.filter(status__exact='a').count()
  num_authors = Author.objects.all().count()
  num_genres = Genre.objects.all().count()
  num_books_contain_guide = Book.objects.filter(title__icontains='guide').count()

  num_visits = request.session.get('num_visits', 0)
  request.session['num_visits'] = num_visits + 1

  context = {
    'num_books': num_books,
    'num_instances': num_instances,
    'num_instances_available': num_instances_available,
    'num_authors': num_authors,
    'num_genres': num_genres,
    'num_books_contain_guide': num_books_contain_guide,
    'num_visits': num_visits,
  }

  return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
  model = Book
  template_name = 'book_list.html'
  paginate_by = 10


class BookDetailView(generic.DetailView):
  model = Book
  template_name = 'book_detail.html'


class AuthorListView(generic.ListView):
  model = Author
  template_name = 'author_list.html'


class AuthorDetailView(generic.DetailView):
  model = Author
  template_name = 'author_detail.html'


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
  """Generic class-based view listing books on loan to current user."""
  model = BookInstance
  template_name = 'bookinstance_list_borrowed_user.html'
  paginate_by = 10

  def get_queryset(self):
    return (
      BookInstance.objects.filter(borrower=self.request.user)
        .filter(status__exact='o')
        .order_by('due_back')
    )
  

class AllLoanedBooksListView(PermissionRequiredMixin, generic.ListView):
  """View listing all borrowed books from the library."""
  model = BookInstance
  template_name = 'bookinstance_list_all_borrowed.html'
  permission_required = 'catalog.can_mark_returned'
  
  def get_queryset(self):
    return BookInstance.objects.filter(status__exact='o').order_by('due_back')

from django.shortcuts import render
from django.views import generic
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

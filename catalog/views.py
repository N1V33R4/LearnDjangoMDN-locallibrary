import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required

from .forms import RenewBookForm
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


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk): 
  book_instance = get_object_or_404(BookInstance, pk=pk)

  if request.method == 'POST':
    form = RenewBookForm(request.POST)
    if form.is_valid():
      book_instance.due_back = form.cleaned_data['renewal_date']
      book_instance.save()

      return HttpResponseRedirect(reverse('all-borrowed'))
  else:
    proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
    form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

  context = {
    'form': form,
    'book_instance': book_instance,
  }

  return render(request, 'book_renew_librarian.html', context)


# Generic editing views
class AuthorCreate(PermissionRequiredMixin, CreateView):
  model = Author
  permission_required = 'catalog.can_mark_returned'
  fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
  initial = {'date_of_death': '2020-11-06'}
  template_name = 'author_form.html'


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
  model = Author
  permission_required = 'catalog.can_mark_returned'
  fields = '__all__'
  template_name = 'author_form.html'


class AuthorDelete(PermissionRequiredMixin, DeleteView):
  model = Author
  permission_required = 'catalog.can_mark_returned'
  success_url = reverse_lazy('authors')
  template_name = 'author_confirm_delete.html'


class BookCreate(PermissionRequiredMixin, CreateView):
  model = Book
  permission_required = 'catalog.can_mark_returned'
  fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
  template_name = 'book_form.html'


class BookUpdate(PermissionRequiredMixin, UpdateView):
  model = Book
  permission_required = 'catalog.can_mark_returned'
  fields = '__all__'
  template_name = 'book_form.html'


class BookDelete(PermissionRequiredMixin, DeleteView):
  model = Book
  permission_required = 'catalog.can_mark_returned'
  success_url = reverse_lazy('books')
  template_name = 'book_confirm_delete.html'

# Setup
## virtualenvwrapper
virtualenv using virtualenvwrapper
Allows you to manage virtual environments in one place.  
> for me it's in /User/Envs

Cmd:
- deactivate: exit out of venv
- workon: list all virtual env
- workon env_name: activate specified
- rmvirtualenv env_name: remove env

## django-admin
startproject project_name: create new website

Creates a folder and a subfolder with the project_name  
The subfolder is the entry point of the site(?)

- `__init__.py`: instruct python to treat dir as python package
- settings.py: site settings, including registering apps we create, location of static files, db config...
  - django uses sqlite by default
- urls.py: url to view mappings, often delegating to individual apps 
- wasgi.py: help django communicate with web server(?)
- asgi.py: provide asynchronous standard

## manage.py commands
python manage.py startapp app_name: creates new dir with admin, apps, models, tests, views files.  

Need to register in settings.py in INSTALLED_APPS:
```py
'catalog.apps.CatalogConfig',
```

## Other settings
Timezone: can change to KH, [list](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

SECRET_KEY: used for security, must use .env in prod(?)
DEBUG: should set to false in prod, to not leak sensitive info

DATABASES: refer [here](https://docs.djangoproject.com/en/4.2/ref/settings/#databases)


## Url mapping
can include urls from an app inside the main urls.py
```py
path('catalog/', include('catalog.urls')),
```
> must have /catalog/urls.py 
> first url becomes the **base** of whatever's in /catalog/urls.py

## Db migrations
Whenever you make changes to the models, you need to run 2 commands:
- python manage.py makemigrations: create migrations for all apps 
  - can specify single app
- python manage.py migrate: apply changes to db 

## Test run
python manage.py runserver 


# Using models 
Think of what you want in a database instead of just fields of an object (Odoo exp).  
Selection lists can be models if change is needed.  

## Fields
Implemented as subclasses of `models.Model`

Can inherit other models, but then the database is fucked up.  

Order of the fields affect rendered form, though can be overidden. 

### Common args
- max_length: size of the type 
  - only on CharField(?)
- help_text: text lable of HTML form
  - can include <a>
- verbose_name: name for field, defaulted to capitalized version
- default: default value, can be value or object(?)
- null: bool, store `NULL` in db
- blank: bool, makes field optional 
  - often used with null=True to represent in db correctly 
  - either that or default(?)
- choices: select box options
- primary_key: bool, makes field pk
  - id field will be created if no pk 
  - default type of this field is in `AppNameConfig`

### Common Types 
- CharField: short-to-mid sized fixed length strings. Must specify `max_length`
- TextField: large arbitrary length strings. Can have `max_length` simply for display, db not affected. 
- IntegerField: validate whole int values. 
- DateField, DateTimeField: `date`, `datetime`
  - can set 
    - `auto_now`: bool, update field to current every time model is saved
    - `auto_now_add`: bool, set date when model was first created
- EmailField: store, validate email
- FileField, ImageField: upload files, images 
  - params to determine how and where uploaded files are stored
  - images have additional validation
- AutoField: auto incrementing int
- ForeignKey: many-to-one
- ManyToManyField: many-to-many relation
- OneToOneField: one-to-one, not present in Odoo oddly enough

[More fields](https://docs.djangoproject.com/en/4.2/ref/models/fields/#field-types) 4.0

### Metadata
Meta class inside each model  
ordering: list of field names  
access permissions: 
[more options](https://docs.djangoproject.com/en/4.2/ref/models/options/)
### Methods
should have `__str__` that returns str version of model  
`get_absolute_url` get model detail of what client sees  

## Model management
### Create
like laravel, just create object and call `save()` 
access field: obj.field

### Search
Model.objects
- .all(): all records
- .filter(query=value): where clause 
  ex: title__contains="wild"  
  filter fields of many-to-one record: genre__name__icontains="ficition"  
  can chain as many relationships as you'd like, i.e. type__cover__name__exact="hard"  
  [more on filters](https://docs.djangoproject.com/en/4.2/topics/db/queries/)
- .get(pk=value): one(?)
- .values(): turn result into dictionaries

[QuerySet api](https://docs.djangoproject.com/en/4.0/ref/models/querysets/)


# Django admin site
To see in admin, must register models in `admin.py`  
```py
admin.site.register(Genre)
admin.site.register(Language)
```

## Superuser
to login, user account must is_staff=True
`py manage.py createsuperuser`: user who has all access 

## Advanced config
Can change list view and detail view of each admin interface

```py
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
  pass
```

### List view
change what you see in list view, `list_display` tuple or list
```py
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
  list_display = ('title', 'author', 'display_genre')
```

**Display custom data with functions**: instead of using fields, you can use fn  
`Book` model:  
```py 
def display_genre(self):
  """Create string for genre in admin."""
  return ", ".join(genre.name for genre in self.genre.all()[:3])

display_genre.short_description = "Genre"
```
> i guess you do have to make a query get all related genres
> I question how performant it is. 

**List filters**: list what field you want to filter by, `list_filter`
```py
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
  list_display = ('book', 'status', 'due_back', 'id')
  list_filter = ('status', 'due_back')
```

### Detail view
**Layout**: `fields`, tuple inside the list are laid horiontally
```py
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
  list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')

  fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
```

**Sectioning**: `fieldsets`, can have section name or None
```py
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
  list_display = ('book', 'status', 'due_back', 'id')
  list_filter = ('status', 'due_back')

  fieldsets = (
    (None, {
      'fields': ('book', 'imprint', 'id'),
    }),
    ('Availability', {
      'fields': ('status', 'due_back'),
    }),
  )
```

**Inline editing associated records**: for relations, can make them show up 
1. Create ModelInline that inherits from either `StackedInline` or `TabularInline`
2. use `inlines` in main Model
```py
class BookInstanceInline(admin.TabularInline): 
  model = BookInstance
  extra = 0


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
  list_display = ('title', 'author', 'display_genre')

  inlines = [BookInstanceInline]
```
> by default, 3 empty records are shown. Add `extra = 0` to remove those useless bastards.

See more in [admin site](https://docs.djangoproject.com/en/4.2/ref/contrib/admin/)

**Many to many field type**: can use the better widget via
```py
filter_horizontal = ('genre',)
```


# Creating our home page
## Url resources
- `catalog/` - home (index) page
- `catalog/books/` - a list of all books
- `catalog/authors/` - a list of all authors
- `catalog/book/<id>/` - detail view of a particular book
- `catalog/author/<id>/` - detail view of specific author
## Index
### Url mapping
since we addded `catalog/` to main `urls.py`, we can simply use `''` for index
*catalog/urls.py*
```py
urlpatterns = [
  path('', views.index, name='index'),
]
```
Names are useful for when we reference them. Any changes in the path will be reflected without changing template.
### View function-based
Functions that query database, render template and return HttpResponse. 
```py
def index(request):
  """View function for home page of site."""

  num_books = Book.objects.all().count()
  ...

  context = {
    'num_books': num_books,
    ...
  }

  return render(request, 'index.html', context=context)
```
`context` is how we pass data to the templates. 
### Template
`render()` will expect to find templates in `locallibary/catalog/templates`
#### Extending
Use blocks. Blocks can have defaults, or be empty for extending. 
> very easy to understand, more so than Laravel
#### Base template
Whatever we need: links, static, site structure. With one content block. 
[base_generic.html](./locallibrary/catalog/templates/base_generic.html)
#### Index template
Fills out the empty blocks, can override default ones. Extends base. 
[index.html](./locallibrary/catalog/templates/index.html)

To use data passed in via context, `{{ data_name }}`  
Extend, block:  
```html
{% extends 'base_generic.html' %}

{% block title %}
  <title>Home page of Local Library</title>
{% endblock title %}
```
### Referencing static files
Location for these files might change in dev vs. prod.  
Can use by specifying location relative to `STATIC_URL`. Need load static tag. 
```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/styles.css' %}" />
```
If STATIC_URL is 'static/', resulting url above will be http://127.0.0.1:8000/static/css/style.css  
Can clash names with different apps(?)
[read more](https://docs.djangoproject.com/en/4.2/howto/static-files/)
### Linking to Urls
```html
<li><a href="{% url 'index' %}">Home</a></li>
```
### Where to find templates config
`TEMPLATES` in `settings.py`


# Generic list and detail views
using class-based views 
## Book list
list all books, name and author 
### Url mapping
```py
path('books/', views.BookListView.as_view(), name='books'),
```
> as_view() to create instance and handle the request
### View (class)
less code than manual function handler  
inherits from `generic.ListView`  
```py
class BookListView(generic.ListView):
  model = Book
  template_name = 'book_list.html'
```
Above handler will query all books and render with the provided template  
&emsp;template should be in app/templates/

**Change default behavior**: 
- context_obj_name: what the variable will be called in template
- queryset: what the queried list will contain
```py
context_object_name = 'book_list' 
queryset = Book.objects.filter(title__icontains='war')[:5]
```

**Overriding methods**: 
- get_queryset(): same as queryset but you can do more(?)
- get_context_data(): add more data to be sent to template
```py
def get_queryset(self):
  return Book.objects.filter(title__icontains='war')[:5]

def get_context_data(self, **kwargs):
  context = super(BookListView, self).get_context_data(**kwargs)
  context['some_data'] = 'This is just some data'
  return context
```
[Extend generic view](https://docs.djangoproject.com/en/4.2/topics/class-based-views/generic-display/)

### List view template
extend base, loop over books to display
```html
{% extends 'base_generic.html' %}

{% block content %}
  <h1>Book List</h1>
  {% if book_list %}
    <ul>
      {% for book in book_list %}
        <li>
          <a href="{{ book.get_absolute_url }}">{{ book.title }}</a>
          ({{ book.author }})
        </li>
      {% endfor %}
    </ul>
  {% else %}
    <p>There are no books in the library.</p>
  {% endif %}
{% endblock content %}
```
#### if
```py
{% if condition %}
{% elif condition %}
{% else %}
{% endif %}
```
#### for
```py
{% for item in list %}
{% empty %}
{% endfor %}
```
Or use if with loop
```html
{% if book_list %}
  <ul>
    {% for book in book_list %}
    {% endfor %}
  </ul>
{% else %}
  <p>There are no books in the library.</p>
{% endif %}
```
[More template tags](https://docs.djangoproject.com/en/4.2/ref/templates/builtins/)
#### Variable access
With each obj of a model, we have access to all its attributes. Including properties and methods!!! 

## Book detail
have id 
### Url mapping
syntax `<something>`
**generic class expects a parameter named `pk`**
```py
path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
```
[Converters](https://docs.djangoproject.com/en/4.2/topics/http/urls/#path-converters): 
- str
- int 
- slug
- uuid
- path: any non-empty str, matches complete url path (with /)

#### Advanced path matching/regular expr
`re_path()`
```py
re_path(r'^book/(?P<pk>\d+)$', views.BookDetailView.as_view(), name='book-detail'),
```
symbol         | meaning
---------------|------------------------------------------------------
^              | match beginning of text
&              | match end of text
\d             | match digit (0-9)
\w             | match word
+              | one of more of the preceding char
*              | zero of more of the preceding char
()             | capture pattern inside
(?P\<name>...) | capture pattern, put value in name to pass to handler
[]             | match against one char in set(?)

> captured values are always string

Examples:
- r'^book/(?P<pk>\d+)$' : /book/1234
- r'^book/(\d+)$' : /book/1234, but pass '1234' as unnamed
- r'^book/(?P<stub>[-\w]+)$' : /book/the-secret-garden
  has one or more chars that are either '-' or word

#### Additional options in url map
```py
path('myurl/<fish>', views.my_view, {'my_template_name': 'some_path'}, name='aurl'),
```
### View (class)
```py
class BookDetailView(generic.DetailView):
  model = Book
  template_name = 'book_detail.html'
```
**Function-based example**: 
```py
def book_detail_view(request, primary_key):
  try:
    book = Book.objects.get(pk=primary_key)
  except Book.DoesNotExist:
    raise Http404('Book does not exist')

  return render(request, 'catalog/book_detail.html', context={'book': book})
```
OR 
```py
from django.shortcuts import get_object_or_404

def book_detail_view(request, primary_key):
  book = get_object_or_404(Book, pk=primary_key)
  return render(request, 'catalog/book_detail.html', context={'book': book})
```
### Detail view template
genre is many-to-many so we can pipe to `|join:", "` to display genre names
```html
{% extends 'base_generic.html' %}

{% block content %}
  <h1>Title: {{ book.title }}</h1>

  <p><strong>Author:</strong> <a href="{{ book.author.get_absolute_url }}">{{ book.author }}</a></p>
  <p><strong>Summary:</strong> {{ book.summary|linebreaksbr }}</p>
  <p><strong>ISBN:</strong> {{ book.isbn }}</p>
  <p><strong>Language:</strong> {{ book.language }}</p>
  <p><strong>Genre:</strong> {{ book.genre.all|join:", " }}</p>

  <div style="margin-left: 20px;margin-top: 20px;">
    <h4>Copies</h4>
    {% for copy in book.bookinstance_set.all %}
      <hr>
      <p class="
        {% if copy.status == 'a' %}
          text-success
        {% elif copy.status == 'm' %}
          text-danger
        {% else %}
          text-warning
        {% endif %}"
      >
        {{ copy.get_status_display }}
      </p>

      {% if copy.status != 'a' %}
        <p><strong>Due to be returned:</strong> {{ copy.due_back }}</p>
      {% endif %}

      <p><strong>Imprint:</strong> {{ copy.imprint }}</p>
      <p class="text-muted"><strong>Id:</strong> {{ copy.id }}</p>
    {% empty %}
      <p>No copies to display.</p>
    {% endfor %}
  </div>
{% endblock content %}
```

**Generated one-to-many function**: bookinstance has one-to-many relation with book  
We can access book instances via `book.bookinstance_set.all`  function
Syntax: `_set`, e.g. `Book` has `bookinstance_set()`
```py
{% for copy in book.bookinstance_set.all %}
```
[Related objects](https://docs.djangoproject.com/en/4.2/topics/db/queries/#related-objects)
**Choices field function**: to get full name of selection field
```py
{{ copy.get_status_display }}
```

Other helpful pipes: 
- join:", "
- linebreaksbr
- default:value
- truncatewords:int

## Pagination
easier to do in class-based views
### View (class)
add `paginate_by`
```py
class BookListView(generic.ListView):
  model = Book
  template_name = 'book_list.html'
  paginate_by = 10
```
works via GET parameters `/catalog/books/?page=2`
### Template
add the previous and next links  
add pagination block in [base](./catalog/templates/base_generic.html), right after content block ends
```html
{% block content %}{% endblock %}
        
{% block pagination %}
  {% if is_paginated %}
    <div class="pagination">
      <span class="page-links">
        {% if page_obj.has_previous %}
          <a href="{{ request.path }}?page={{ page_obj.previous_page_number }}">previous</a>
        {% endif %}

        <span class="page_current">
          Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}
        </span>

        {% if page_obj.has_next %}
          <a href="{{ request.path }}?page={{ page_obj.next_page_number }}">next</a>
        {% endif %}
      </span>
    </div>
  {% endif %}
{% endblock pagination %}
```
- `page_obj` is instance of `Paginator`
- `request` exists in template(?)


# Sessions framework

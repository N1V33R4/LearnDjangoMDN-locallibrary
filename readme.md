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

from django.contrib import admin

from .models import Book, Author, Genre, BookInstance, Language

# Register your models here.
# admin.site.register(Book)
# admin.site.register(Author)
# admin.site.register(BookInstance)
# admin.site.register(Language)
# admin.site.register(Genre)


class BookInstanceInline(admin.TabularInline): 
  model = BookInstance
  extra = 0


class BookInline(admin.StackedInline):
  model = Book
  extra = 0

  filter_horizontal = ('genre',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
  list_display = ('name', 'book_count')


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
  list_display = ('name', 'book_count')


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
  list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')

  fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
  # exclude = ['date_of_death']
  inlines = [BookInline]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
  list_display = ('title', 'author', 'display_genre')
  filter_horizontal = ('genre',)

  inlines = [BookInstanceInline]


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
  list_display = ('book', 'status', 'borrower', 'due_back', 'id')
  list_filter = ('status', 'due_back')

  fieldsets = (
    (None, {
      'fields': ('book', 'imprint', 'id'),
    }),
    ('Availability', {
      'fields': ('status', 'due_back', 'borrower'),
    }),
  )

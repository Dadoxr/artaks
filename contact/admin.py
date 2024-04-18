from django.contrib import admin

from contact.models import Contact

@admin.register(Contact)
class UserAdmin(admin.ModelAdmin):
    ordering = ['pk']
    list_display = ('pk', 'abc', 'start', 'end', 'operator', 'region', 'territory', 'inn')
    search_fields = ('pk', 'abc', 'start', 'end', 'operator', 'region', 'territory', 'inn')


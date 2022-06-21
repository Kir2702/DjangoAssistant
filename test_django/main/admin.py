from django.contrib import admin
from.models import Templates



class TemplatesAdmin(admin.ModelAdmin):
    list_display = ('title', )
    list_display_links = ('title', )
    search_fields = ('title', 'content', )

admin.site.register (Templates, TemplatesAdmin)
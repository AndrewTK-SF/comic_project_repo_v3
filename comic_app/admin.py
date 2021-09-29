from django.contrib import admin
from .models import User
from comic_app.models import User, Comic, Collection

class UserAdmin(admin.ModelAdmin):
    pass
admin.site.register(User, UserAdmin)

class ComicAdmin(admin.ModelAdmin):
    pass
admin.site.register(Comic, UserAdmin)

class ComicAdmin(admin.ModelAdmin):
    pass
admin.site.register(Collection, UserAdmin)



# Register your models here.

# Register your models here.

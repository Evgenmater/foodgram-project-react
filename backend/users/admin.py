from django.contrib import admin

from users.models import Subscription, User


class UserAdmin(admin.ModelAdmin):

    list_filter = ('email', 'first_name')


admin.site.register(User, UserAdmin)
admin.site.register(Subscription)

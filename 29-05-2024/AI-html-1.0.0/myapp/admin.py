from django.contrib import admin
from .models import User,WorkSpace,Uploadfiles,Onboard,Admin_user,Pricing,Feedback
admin.site.register(User)
admin.site.register(WorkSpace)
admin.site.register(Feedback)
admin.site.register(Uploadfiles)
admin.site.register(Onboard)
admin.site.register(Admin_user)
admin.site.register(Pricing)
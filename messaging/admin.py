from django.contrib import admin
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered
from .models import MessageThread, Message

try:
    admin.site.register(MessageThread)
    admin.site.register(Message)
except AlreadyRegistered:
    pass

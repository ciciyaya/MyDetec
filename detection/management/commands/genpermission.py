# coding: utf-8
__author__ = 'ciciya'

# import sys
# sys.path.append("/home/ciciya/PycharmProjects/book_example/8_full_android_malware_detection")
# import os
# os.environ["DJANGO_SETTINGS_MODULE"] = "android_malware_detection.settings"

import os
from bs4 import BeautifulSoup
from detection.models import *
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    FILE_PATH = os.path.join(settings.MEDIA_ROOT, "manifest.xml")

    def handle(self, *arg, **options):
        Permission.objects.all().delete()
        content = self.get_file_content()
        permissions = self.get_permissions(content)
        for permission in permissions:
            permission_object = Permission(name=permission['name'], protectionLevel=permission['protectionLevel'],
                                           permissionGroup=permission['group'])
            permission_object.save()

    def get_file_content(self):
        file = open(self.FILE_PATH, 'r')
        content = file.read()
        return content

    def get_permissions(self, content):
        bs = BeautifulSoup(content)
        permissions = bs.find_all('permission')
        _permissions = []
        for permission in permissions:
            per = {
                'name': permission.attrs.get('android:name', '').split('.')[-1],
                'group': permission.attrs.get('android:permissiongroup', ''),
                'protectionLevel': permission.attrs.get('android:protectionlevel', '')
            }
            _permissions.append(per)
        return _permissions

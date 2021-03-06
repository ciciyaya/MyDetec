# coding:utf-8
import xadmin
from xadmin import views
from models import *

from DjangoUeditor.models import UEditorField
from DjangoUeditor.widgets import UEditorWidget
from xadmin.views import BaseAdminPlugin, ModelFormAdminView, DetailAdminView
from django.conf import settings
from django.db.models import TextField


class GlobalSetting(object):
    # 设置base_site.html的Title
    site_title = 'Android Malware Detection Admin'

    def get_site_menu(self):
        return (
            {'title': '应用管理', 'menus': (
                {'title': '检测结果', 'icon': 'fa fa-train', 'url': self.get_model_url(DeteR, 'changelist')},
                {'title': '应用数据', 'icon': 'fa fa-train', 'url': self.get_model_url(ApkPermission, 'changelist')},
                {'title': '检测模型', 'icon': 'fa fa-train', 'url': self.get_model_url(MLModel, 'changelist')},
                {'title': '权限数据', 'icon': 'fa fa-train', 'url': self.get_model_url(Permission, 'changelist')},
            )},

        )


class PermissionAdmin(object):
    list_display = ['name', 'protectionLevel', 'permissionGroup']
    search_fields = ['name']
    list_per_page = 20


class APKPermissionsAdmin(object):
    list_display = ['package', 'isMalware', 'INTERNET', 'READ_CONTACTS', 'WRITE_CONTACTS', 'READ_CALENDAR',
                    'WRITE_CALENDAR', 'SEND_SMS', 'RECEIVE_SMS', 'READ_SMS', 'RECEIVE_WAP_PUSH', 'RECEIVE_MMS']
    search_fields = ['package']
    list_per_page = 50
    # ordering = ['isMalware']


class MLModelsAdmin(object):
    list_display = ['time', 'knn', 'nb', 'lr', 'rf', 'svm']
    list_per_page = 50
    ordering = ['-time']


class DeteRAdmin(object):
    list_display = ['package', 'r', 'perdict', 'knn', 'nb', 'lr', 'rf', 'svm']
    list_per_page = 50
    ordering = ['-time']
    search_field = ['package']


class XadminUEditorWidget(UEditorWidget):
    def __init__(self, **kwargs):
        self.ueditor_options = kwargs
        self.Media.js = None
        super(XadminUEditorWidget, self).__init__(kwargs)


class UeditorPlugin(BaseAdminPlugin):
    def get_field_style(self, attrs, db_field, style, **kwargs):
        if style == 'ueditor':
            if isinstance(db_field, UEditorField):
                widget = db_field.formfield().widget
                param = {}
                param.update(widget.ueditor_settings)
                param.update(widget.attrs)
                return {'widget': XadminUEditorWidget(**param)}
            if isinstance(db_field, TextField):
                return {'widget': XadminUEditorWidget}
        return attrs

    def block_extrahead(self, context, nodes):
        js = '<script type="text/javascript" src="%s"></script>' % (settings.STATIC_URL + "ueditor/ueditor.config.js")
        js += '<script type="text/javascript" src="%s"></script>' % (settings.STATIC_URL + "ueditor/ueditor.all.min.js")
        nodes.append(js)


xadmin.site.register(views.CommAdminView, GlobalSetting)
xadmin.site.register_plugin(UeditorPlugin, DetailAdminView)
xadmin.site.register_plugin(UeditorPlugin, ModelFormAdminView)
xadmin.site.register(Permission, PermissionAdmin)
xadmin.site.register(ApkPermission, APKPermissionsAdmin)
xadmin.site.register(MLModel, MLModelsAdmin)
xadmin.site.register(DeteR, DeteRAdmin)

# coding:utf-8
import os
import random
from datetime import datetime

import simplejson as json
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

import libs as LIB
from models import *


# 首页
def Index(request):
    context = RequestContext(request)
    context_dict = {}

    deteObjs = DeteR.objects.order_by('-time')[0:20]
    context_dict['results'] = deteObjs

    return render_to_response('detection/index.html', context_dict, context)


# 上传文件
def UploadAPK(request):
    response_dict = {
        'code': -1,
        'msg': 'unkown'
    }
    if request.method == 'POST':
        file_obj = request.FILES.get('apk', None)
        if file_obj is not None:
            savePath = os.path.join(settings.MEDIA_ROOT, 'upload/' + datetime.now().strftime('%Y%m%d%H%M%S') + str(
                random.randint(0, 100000)) + '.apk')
            apkFile = open(savePath, 'wb+')
            for chunk in file_obj.chunks():
                apkFile.write(chunk)
            apkFile.close()

            if LIB.detect(savePath):
                response_dict['code'] = 1
            else:
                response_dict['code'] = -1
                response_dict['msg'] = '文件不合法'
        else:
            response_dict['code'] = -1
            response_dict['msg'] = '文件不合法'

    return HttpResponse(json.dumps(response_dict), content_type="application/json")


# chart数据
def IndexChart(request):
    response_dict = {}
    model = MLModel.objects.order_by('-time')[0]
    response_dict['knn'] = [{'name': u'准确率', 'y': model.knn}, {'name': u'误判率', 'y': 100 - model.knn}]
    response_dict['nb'] = [{'name': u'准确率', 'y': model.nb}, {'name': u'误判率', 'y': 100 - model.nb}]
    response_dict['lr'] = [{'name': u'准确率', 'y': model.lr}, {'name': u'误判率', 'y': 100 - model.lr}]
    response_dict['rf'] = [{'name': u'准确率', 'y': model.rf}, {'name': u'误判率', 'y': 100 - model.rf}]
    response_dict['svm'] = [{'name': u'准确率', 'y': model.svm}, {'name': u'误判率', 'y': 100 - model.svm}]

    return HttpResponse(json.dumps(response_dict), content_type="application/json")

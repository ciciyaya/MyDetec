from androguard.core.bytecodes.apk import *
from models import *
from sklearn.externals import joblib
from django.conf import settings
import os
import numpy as np

MODELS_PATH = os.path.join(settings.MEDIA_ROOT, 'models')


def detect(file_path):
    apk = APK(file_path)
    if apk.is_valid_APK():
        apkObj = DP(apk)
        datas = []
        all_field_names = getFieldNames()
        datas.append([int(getattr(apkObj, field_name)) for field_name in all_field_names])
        datas = np.array(datas)
        knn = DKNN(datas)
        nb = DNB(datas)
        lr = DLR(datas)
        rf = DRF(datas)
        svm = DSVM(datas)

        modelObj = MLModel.objects.order_by('-time')[0]
        perdict = (modelObj.knn * knn + modelObj.nb * nb + modelObj.lr * lr + modelObj.rf * rf + modelObj.svm * svm) / 5
        result = 0
        if perdict >= 40:
            result = 1

        deteObj = DeteR(package=apkObj.package, r=result, knn=knn, nb=nb, lr=lr, rf=rf, svm=svm, perdict=perdict)
        deteObj.save()

        return True
    else:
        return False


def DKNN(datas):
    model_path = os.path.join(MODELS_PATH, 'KNN.model')
    model = joblib.load(model_path)
    results = model.predict(datas)
    return int(results[0])


def DNB(datas):
    model_path = os.path.join(MODELS_PATH, 'KNN.model')
    model = joblib.load(model_path)
    results = model.predict(datas)
    return int(results[0])


def DLR(datas):
    model_path = os.path.join(MODELS_PATH, 'LR.model')
    model = joblib.load(model_path)
    results = model.predict(datas)
    return int(results[0])


def DRF(datas):
    model_path = os.path.join(MODELS_PATH, 'RF.model')
    model = joblib.load(model_path)
    results = model.predict(datas)
    return int(results[0])


def DSVM(datas):
    model_path = os.path.join(MODELS_PATH, 'SVM.model')
    model = joblib.load(model_path)
    results = model.predict(datas)
    return int(results[0])


def DP(apk):
    all_permissions = get_permissions()
    args = {}
    # package = apk.filename
    package = apk.get_package()
    args['package'] = package
    permissions = apk.get_permissions()

    for p in permissions:
        p = p.split('.')[-1]
        if all_permissions.has_key(p):
            args[p] = 1

    apkObjs = DetectionPermission.objects.filter(package__exact=package)
    if not apkObjs:
        apkObj = DetectionPermission(**args)
        apkObj.save()
        return DetectionPermission.objects.get(package=package)
    else:
        apkObj = apkObjs[0]
        return apkObj


def get_permissions():
    all_permission = {}
    permissions = Permission.objects.all()
    for p in permissions:
        all_permission[p.name] = {'protectionLevel': p.protectionLevel, 'permissionGroup': p.permissionGroup}
    return all_permission


def getFieldNames():
    all_field_names = ApkPermission._meta.get_all_field_names()
    all_field_names.remove(u'id')
    all_field_names.remove('package')
    all_field_names.remove('isMalware')
    return all_field_names

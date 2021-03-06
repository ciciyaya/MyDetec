# coding: utf-8
import random

__author__ = 'ciciya'

from django.core.management.base import BaseCommand
from detection.models import *
from django.conf import settings

import os
import numpy as np
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.externals import joblib


class Command(BaseCommand):
    FEATURE_DATA = []
    LABELS = []
    MALWARE_APPS = 0
    NORMAL_APPS = 0
    MODELS_PATH = os.path.join(settings.MEDIA_ROOT, 'models')

    def handle(self, *arg, **options):
        self.loadDatas()
        index = [i for i in range(len(self.FEATURE_DATA))]
        random.shuffle(index)
        self.FEATURE_DATA = self.FEATURE_DATA[index]
        self.LABELS = self.LABELS[index]
        print(self.FEATURE_DATA.shape)
        print(self.LABELS.shape)
        # self.FEATURE_DATA = np.random.randint(0, 2, size=[13053, 314])
        # self.LABELS = np.random.randint(0, 2, size=[13053, 1])
        # 特征取30,31,32差别特别大
        train_data, test_data, train_labels, test_labels = train_test_split(self.FEATURE_DATA, self.LABELS,
                                                                            test_size=0.2)

        knn_accuracy = 100 * self.KNNModel(train_data, test_data, train_labels, test_labels)
        nb_accuracy = 100 * self.NBModel(train_data, test_data, train_labels, test_labels)
        lr_accuracy = 100 * self.LRModel(train_data, test_data, train_labels, test_labels)
        rf_accuracy = 100 * self.RFModel(train_data, test_data, train_labels, test_labels)
        svm_accuracy = 100 * self.SVMModel(train_data, test_data, train_labels, test_labels)

        model_obj = MLModel(malware=self.MALWARE_APPS, normal=self.NORMAL_APPS, knn=knn_accuracy, nb=nb_accuracy,
                            lr=lr_accuracy, rf=rf_accuracy, svm=svm_accuracy)
        model_obj.save()
        print('all models saved')

    def KNNModel(self, train_data, test_data, train_labels, test_labels):
        model = KNeighborsClassifier()
        model.fit(train_data, train_labels)
        self.saveModel(model, 'KNN')
        predict = model.predict(test_data)
        print(test_labels)
        print(predict)
        return metrics.accuracy_score(test_labels, predict)

    def NBModel(self, train_data, test_data, train_labels, test_labels):
        model = MultinomialNB(alpha=0.01)
        model.fit(train_data, train_labels)
        self.saveModel(model, 'NB')
        predict = model.predict(test_data)
        print(predict)
        return metrics.accuracy_score(test_labels, predict)

    def LRModel(self, train_data, test_data, train_labels, test_labels):
        model = LogisticRegression(penalty='l2')
        model.fit(train_data, train_labels)
        self.saveModel(model, 'LR')
        predict = model.predict(test_data)
        print(predict)
        return metrics.accuracy_score(test_labels, predict)

    def RFModel(self, train_data, test_data, train_labels, test_labels):
        model = RandomForestClassifier(n_estimators=8)
        model.fit(train_data, train_labels)
        self.saveModel(model, 'RF')
        predict = model.predict(test_data)
        print(predict)
        return metrics.accuracy_score(test_labels, predict)

    def SVMModel(self, train_data, test_data, train_labels, test_labels):
        model = SVC(kernel='rbf', probability=True)
        model.fit(train_data, train_labels)
        self.saveModel(model, 'SVM')
        predict = model.predict(test_data)
        print(predict)
        return metrics.accuracy_score(test_labels, predict)

    def saveModel(self, model, name):
        dump_path = os.path.join(self.MODELS_PATH, name + '.model')
        joblib.dump(model, dump_path)

    def loadDatas(self):
        all_field_names = self.getFieldNames()
        # print(all_field_names[32])
        apkinfos = ApkPermission.objects.all()
        datas = []
        labels = []
        malware = 0
        normal = 0
        for apkinfo in apkinfos:
            datas.append([int(getattr(apkinfo, field_name)) for field_name in all_field_names])
            labels.append(apkinfo.isMalware)
            if apkinfo.isMalware == 1:
                malware += 1
            else:
                normal += 1

        self.MALWARE_APPS = malware
        self.NORMAL_APPS = normal
        self.FEATURE_DATA = np.array(datas)
        self.LABELS = np.array(labels)

    def getFieldNames(self):
        all_field_names = ApkPermission._meta.get_all_field_names()
        all_field_names.remove(u'id')
        all_field_names.remove('package')
        all_field_names.remove('isMalware')
        return all_field_names

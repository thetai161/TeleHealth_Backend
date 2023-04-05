from django.shortcuts import render
from tlc.models import *
import numpy as np
from datetime import datetime
import shutil
import os
from base.message import success
# Create your views here.


def load_result(request, id):
    detailId = id
    listDetail = ResultFile.objects.get(upload_file_id=detailId)
    url = listDetail.url
    x = np.load('./media/' + url + '/x.npy').tolist()
    y = np.load('./media/' + url + '/y.npy').tolist()
    z = np.load('./media/' + url + '/z.npy').tolist()
    d = np.load('./media/' + url + '/d.npy').tolist()
    e = np.load('./media/' + url + '/e.npy').tolist()
    f = np.load('./media/' + url + '/f.npy').tolist()
    context = {'right_lung': listDetail.right_lung,
               'left_lung': listDetail.left_lung,
               'lung_volume': listDetail.lung_volume,
               'x': x, 'y': y, 'z': z, 'd': d, 'e': e, 'f': f,
               }
    return render(request, 'result.html', context)

import numpy as np
from glob import glob
from datetime import datetime
import shutil
import os
from base.message import success
import os
import cv2
from django.http import HttpResponse
from tlc.models import FileTLC
from tensorflow.keras.models import load_model
from rest_framework.views import APIView
from tlc.serializers import FileSerializer
from doctor.models import Doctor
from patient.serializers import PatientSerializer
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from authentication.mixins import GetSerializerClassMixin
from .models import PcModel
from .serializers import PcSerializer
from rest_framework import generics, status, permissions
from base.message import success, error

from authentication.models import User
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from authentication.permissions import Role1, Role2, Role3, Role4, Role1or3


class PcViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions
    """
    queryset = PcModel.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = PcSerializer

    def pc_load(self, request):
        id = request.user.id
        patientId = request.data['patientId']
        if request.method == "POST":
            uploaded_files = request.FILES.getlist("uploadfiles")
            urlk = str(datetime.today().year) + str(datetime.today().month) + str(datetime.today().day) + \
                str(datetime.now().hour)+str(datetime.now().minute) + \
                str(datetime.now().second) + str(id) + 'pc'
            Folder = './media/'+urlk
            os.makedirs(Folder)
            for uploaded_file in uploaded_files:
                FileTLC(f_name=urlk,
                        myfiles=uploaded_file, user_id=id).save()
            for uploaded_file in uploaded_files:
                uploaded_file_name = str(uploaded_file)
                global server_store_path
                uploaded_file_path = './media/' + uploaded_file_name
                server_store_path = './media/' + urlk
                shutil.move(uploaded_file_path, server_store_path)
            png_path =glob(server_store_path+'/*')
            for i in png_path:
                global name_image
                name_image = os.path.basename(i)
            model_path = './pc/PC_Trained/mode_new.h5'
            model_saved = load_model(model_path)
            def predict(image_path):

                img = cv2.imread(image_path)
                img = cv2.resize(img, (256, 256))

                preds = model_saved.predict(np.expand_dims(img, axis=0))[0]
                label = np.argmax(preds)

                if label == 1:
                    result = False
                    return result
                else:
                    result = True
                    return result

            image_path = server_store_path+'/'+name_image
            result = predict(image_path)
            for uploaded_file in uploaded_files:
                PcModel(result=result,
                        file=uploaded_file, patient_id=patientId).save()
            image = FileTLC.objects.filter(f_name=urlk)
            imageSerializer = FileSerializer(image, many=True)
            context = {
                'result': result,
                'image': imageSerializer.data
            }
            return success(data=context)
        
    def get_result_by_patient_id(self, request):
        patientId = self.request.GET.get('pk')
        pc = PcModel.objects.filter(patient_id=patientId)
        pcSerializer = PcSerializer(pc, many=True)
        return success(data=pcSerializer.data)

from django.shortcuts import render
from rest_framework.decorators import action
from authentication.mixins import GetSerializerClassMixin
from tlc.serializers import ResultFileSerializer, UserUploadedFileSerializer
from .models import *
import numpy as np
from glob import glob
from datetime import datetime
import shutil
import os
from base.message import success, error
from .utils2 import load_data
from authentication.permissions import Role1, Role2, Role3, Role4, Role1or3
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated


class LoadFileViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserUploadedFileSerializer

    def post_file(self, request):
        request_user = request.user.id
        patientId = request.data['patientId']
        id = request.user.id
        if request.method == "POST":
            uploaded_files = request.FILES.getlist("uploadfiles")
            urlk = str(datetime.today().year) + str(datetime.today().month) + str(datetime.today().day) + \
                str(datetime.now().hour)+str(datetime.now().minute) + \
                str(datetime.now().second) + str(id)
            Folder = './media/'+urlk
            os.makedirs(Folder)
            # gauth = GoogleAuth()
            # drive = GoogleDrive(gauth)
            userob = User.objects.get(id=request_user)
            for uploaded_file in uploaded_files:
                FileTLC(f_name=request_user,
                        myfiles=uploaded_file, user=userob).save()
            for uploaded_file in uploaded_files:
                uploaded_file_name = str(uploaded_file)
                global server_store_path
                uploaded_file_path = './media/' + uploaded_file_name
                server_store_path = './media/' + urlk
                shutil.move(uploaded_file_path, server_store_path)
            # entries = os.scandir(Folder)
            # upload_files = []
            # for entry in entries:
            #     print(entry.name)
            #     k = str(entry.name)
            #     upload_files.append(os.path.join(Folder, k))
            # folder_name = urlk
            # folder = drive.CreateFile({'title': folder_name, 'mimeType': 'application/vnd.google-apps.folder'})
            # folder.Upload()
            # print('File ID: %s' % folder.get('id'))
            # folder_id = str(folder.get('id'))
            # for upload_file in upload_files:
            #     gfile = drive.CreateFile({'parents': [{'id': folder_id}]})
            #     gfile.SetContentFile(upload_file)
            #     gfile.Upload()  # Upload the file.
            #     print('success')
            # folder_contents = UserUploadedFile.objects.all()
            # folder_contents.delete()
            data_path = server_store_path
            # export result to other folder
            # open dicom files
            g = glob(data_path + '/*.dcm')
            output_path = working_path = 'test'
            # loop over the image files and store everything into a list
            right_mask, left_mask, volume, z = load_data(
                Folder, patientId, urlk)
            k1 = len(z)
            h1 = 3 * k1
            x1 = z[:, :, 0].reshape(-1)
            y1 = z[:, :, 1].reshape(-1)
            z1 = z[:, :, 2].reshape(-1)
            np.save('./media/'+urlk+'/x.npy', x1)
            np.save('./media/'+urlk+'/y.npy', y1)
            np.save('./media/'+urlk+'/z.npy', z1)
            d1 = np.arange(0, h1, 3)
            e1 = np.arange(1, h1, 3)
            f1 = np.arange(2, h1, 3)
            np.save('./media/'+urlk+'/d.npy', d1)
            np.save('./media/'+urlk+'/e.npy', e1)
            np.save('./media/'+urlk+'/f.npy', f1)

            context = {
                'right_lung': right_mask,
                'left_lung': left_mask,
                'lung_volume': volume,
            }
            return success(data=context)

    def get_result_by_patient_id(self, request):
        patientId = self.request.GET.get('pk')
        tlc = UserUploadedFile.objects.filter(patient_id=patientId)
        tlcSerializer = UserUploadedFileSerializer(tlc, many=True)
        return success(data=tlcSerializer.data)

    def detail_result(self, request):
        userUploadFileId = self.request.GET.get('pk')
        tlcResult = ResultFile.objects.get(upload_file_id=userUploadFileId)
        tlcResultSerializer = ResultFileSerializer(tlcResult)
        return success(data=tlcResultSerializer.data)

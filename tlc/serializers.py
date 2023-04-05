
from rest_framework import serializers
from .models import ResultFile, UserUploadedFile, FileTLC


class ResultFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultFile
        fields = '__all__'


class UserUploadedFileSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            resultFile = ResultFile.objects.get(upload_file_id=instance.id)
            resultInfo = ResultFileSerializer(resultFile).data
        except:
            resultInfo = ""

        representation['result'] = resultInfo

        return representation

    class Meta:
        model = UserUploadedFile
        fields = '__all__'

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileTLC
        fields = '__all__'
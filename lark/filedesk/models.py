from django.db import models


class FileObject(models.Model):

    file_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    file_name = models.CharField( 
        max_length=100,
        validators=[]
    )

    file_url = models.CharField(
        max_length = 255,
    )

    is_folder = models.BooleanField(
        default=False,
    )

    folder_content = models.ForeignKey(FileObject, on_delete=models.CASCADE) 

    def get_file_json(self):
        # return a json format of file object
        if self.is_folder:
            return "" 
        else:
            return self.folder_content_set.all()

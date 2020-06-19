from django.db import models


def content_file_name(instance, filename):
    return '/'.join(['instructions', instance.sachnr, filename])


class Instructions(models.Model):
    sachnr = models.CharField(max_length=255, unique=True)
    kk_docs = models.FileField(upload_to=content_file_name, blank=True, null=True)
    malta = models.FileField(upload_to=content_file_name, blank=True, null=True)
    packing = models.FileField(upload_to=content_file_name, blank=True, null=True)
    soldering = models.FileField(upload_to=content_file_name, blank=True, null=True)
    heating = models.FileField(upload_to=content_file_name, blank=True, null=True)
    drawing = models.FileField(upload_to=content_file_name, blank=True, null=True)
    sab_control = models.FileField(upload_to=content_file_name, blank=True, null=True)
    sab_soldering = models.FileField(upload_to=content_file_name, blank=True, null=True)

    class Meta:
        permissions = (
            ("view_instructions_app", "Can see app"),
        )
        verbose_name_plural = "instructions"

    def __str__(self):
        return self.sachnr

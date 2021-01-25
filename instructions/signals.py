from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
import os

import shutil

from instructions.models import Instructions
from django3_apps.settings import BASE_DIR



@receiver(pre_save, sender=Instructions, dispatch_uid="pre_save_my_handler")
def my_handler(sender, **kwargs):
    print("changing files")
    instance = kwargs['instance']
    try:
        original_object = Instructions.objects.get(pk=instance.pk)
    except:
        return
    if original_object:
        field_names = [field.name for field in original_object._meta.fields]

        for field in field_names:
            try:
                ori_field = getattr(original_object, field)
                new_field = getattr(instance, field)
                if ori_field != new_field:
                    os.remove(ori_field.path)
            except:
                return


@receiver(pre_delete, sender=Instructions, dispatch_uid="delete_file")
def delete_file(instance, **kwargs):
    attachments = {instance.malta, instance.packing, instance.soldering, instance.heating, instance.drawing,
                   instance.sab_control, instance.sab_soldering}
    for n in attachments:
        n.delete()


@receiver(pre_delete, sender=Instructions, dispatch_uid="delete_folder")
def delete_folder(instance, **kwargs):
    try:
        path = Instructions.objects.get(pk=instance.pk)
    except:
        return
    if path:
        shutil.rmtree(BASE_DIR+'/site_media/Instructions/'+instance.sachnr+'/')

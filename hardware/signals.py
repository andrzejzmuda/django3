# from django.db.models.signals import pre_delete
# from django.dispatch import receiver

# import shutil

# from models import History
# from django3_apps.settings import BASE_DIR

# @receiver(pre_delete, sender=History, dispatch_uid="delete_file")
# def delete_file(instance, **kwargs):
#     attachments = {instance.attachment}
#     for n in attachments:
#         n.delete()


# @receiver(pre_delete, sender=History, dispatch_uid="delete_folder")
# def delete_folder(instance, **kwargs):
#     try:
#         path = Instructions.objects.get(pk=instance.pk)
#     except:
#         return
#     if path:
#         shutil.rmtree(BASE_DIR+'/site_media/Instructions/'+instance.sachnr+'/')
from django.apps import apps
from django.db.models import Max
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone

from cv.models import CourseOffering


def validate_model(sender, **kwargs):
    kwargs['instance'].full_clean()


for model in apps.get_app_config('cv').get_models():
    pre_save.connect(validate_model, sender=model)


@receiver(post_save, sender=CourseOffering)
def update_last_and_current_offering(sender, **kwargs):
    offering = kwargs.get('instance')
    course = offering.course
    course.last_offered = course.courseoffering_set.filter(
        start_date__lte=timezone.now()).aggregate(
        last_offering=Max('end_date'))['last_offering']
    course.save()

from celery import shared_task

@shared_task
def beach_debug_task(self):
    print('Beach Request: {0!r}'.format(self.request))
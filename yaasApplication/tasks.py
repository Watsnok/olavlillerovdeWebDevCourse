from __future__ import absolute_import, unicode_literals
from celery.schedules import crontab
from celery.task import periodic_task
from yaasApplication.models import auction
from django.utils import timezone
from django.db.models import Q


@periodic_task(run_every=crontab(minute="*", hour="*", day_of_week="*"))
def checkAuctions():
    print("Check in")
    all_auctions = auction.objects.filter(Q(is_active=True) and Q(isBanned=False))
    for p in all_auctions:
        if p.deadline <= timezone.now():
            print(timezone.now())
            p.resolveAuction()
            p.save()

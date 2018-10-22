from __future__ import absolute_import, unicode_literals
from celery.schedules import crontab
from celery.task import periodic_task
from yaasApplication.models import auction
from django.utils import timezone
from django.db.models import Q


@periodic_task(run_every=crontab(minute="*", hour="*", day_of_week="*"))
def checkAuctions():
    print("Check in")
    #Auctions locked by users will not be resolved automatically
    all_auctions = auction.objects.filter(Q(is_active=True) and Q(isBanned=False) and Q(lockedby=""))
    for p in all_auctions:
        if p.deadline <= timezone.now():
            print(timezone.now())
            p.resolveAuction()
            p.save()
        #Automated task releases timelock after five minutes. Ticks once every minute for all locked auctions
        if p.lockedby != "":
            if p.getTimeLock() == 5:
                p.lockedby = ""
            else:
                p.incrementTimeLock()
        p.save()


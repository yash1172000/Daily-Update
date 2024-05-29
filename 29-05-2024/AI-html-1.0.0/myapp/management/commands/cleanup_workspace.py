from django.core.management.base import BaseCommand
from django.utils import timezone
from myapp.models import WorkSpace,Pricing 

class Command(BaseCommand):
    help = 'Deletes entries older than one month in the WorkSpace table'
    
    def handle(self, *args, **options):
        pricings = Pricing.objects.all()
        for pricing in pricings:
            price_of_plan = pricing.price_of_plan
        #    print(type(price_of_plan))
            if price_of_plan == 25:
              plan_history_delete = timezone.timedelta(days=30)
            elif price_of_plan == 55:
               plan_history_delete =  timezone.timedelta(days=30)
            elif price_of_plan == 200:
               plan_history_delete =  timezone.timedelta(days=365)
            elif price_of_plan == 500:
               plan_history_delete =  timezone.timedelta(days=365)
            else :
               plan_history_delete =  timezone.timedelta(days=100000000)
            one_month_ago = timezone.now() - plan_history_delete
            WorkSpace.objects.filter(user=pricing.user , created_at__lte=one_month_ago).delete()
            self.stdout.write(self.style.SUCCESS('Successfully deleted old entries in WorkSpace table'))
        # one_month_ago = timezone.now() - timezone.timedelta(days=30)
        # WorkSpace.objects.filter(created_at__lte=one_month_ago).delete()
        # self.stdout.write(self.style.SUCCESS('Successfully deleted old entries in WorkSpace table'))

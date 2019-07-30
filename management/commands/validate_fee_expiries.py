from django.core.management.base import BaseCommand, CommandError
from SyllabusTrackerApp.models import Membership, FeeExpiry

class Command(BaseCommand):
    help = 'Checks for expiries of fee times and send out emails, where necessary.'

#    def add_arguments(self, parser):
#        parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        for member in Membership.objects.all():
            for fee_expiry in member.fees.all():
                self.stdout.write(fee_expiry.fee_definition.name + " expires on "+str(fee_expiry.fee_expiry_date))
import datetime
from django.core.management.base import BaseCommand, CommandError
from SyllabusTrackerApp.models import Membership, FeeExpiry

class Command(BaseCommand):
    help = 'Checks for expiries of fee times and send out emails, where necessary.'

#    def add_arguments(self, parser):
#        parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        for member in Membership.objects.all():
            self.stdout.write(member.user.full_name())
            for fee_expiry in member.fees.all():
                if fee_expiry.fee_expiry_date == None:
                    self.stdout.write("\t- "+fee_expiry.fee_definition.name + " hasn't been set.")
                else:
                    difference = fee_expiry.fee_expiry_date - datetime.date.today()
                    if difference.days < 0:
                        self.stdout.write("\t- "+fee_expiry.fee_definition.name + " is overdue for "+str(abs(difference.days))+" days!")
                        
                    else:
                        self.stdout.write("\t- "+fee_expiry.fee_definition.name + " expires on "+str(fee_expiry.fee_expiry_date))
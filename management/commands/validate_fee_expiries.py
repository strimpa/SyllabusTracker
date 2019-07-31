import datetime
from django.urls import reverse
from django.core.management.base import BaseCommand, CommandError
from SyllabusTrackerApp.models import Membership, FeeExpiry, Notification
from django.core.mail import send_mail
from django.template.loader import render_to_string

class Command(BaseCommand):
    help = 'Checks for expiries of fee times and send out emails, where necessary.'

#    def add_arguments(self, parser):
#        parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        for member in Membership.objects.all():
            self.stdout.write(member.user.username)
            for fee_expiry in member.fees.all():
                if fee_expiry.fee_expiry_date == None:
                    self.stdout.write("\t- "+fee_expiry.fee_definition.name + " hasn't been set.")
                else:
                    difference = fee_expiry.fee_expiry_date - datetime.date.today()
                    if difference.days < 0:
                        self.stdout.write("\t- "+fee_expiry.fee_definition.name + " is overdue for "+str(abs(difference.days))+" days! Sending email!")
                        the_user = member.user

                        text = "Your " + fee_expiry.fee_definition.name + " is overdue for "+str(abs(difference.days))+" days!"
                        link = reverse('profile')
                        notification = Notification.objects.create(user=the_user, text=text, link=link)

                        template_values = {
                            'name':the_user.first_name,
                            'email':the_user.email,
                            'fee_type':fee_expiry.fee_definition.name,
                            'overdue':abs(difference.days),
                        }        
                        msg_plain = render_to_string('fee_expiry_email.txt', template_values)
                        msg_html = render_to_string('fee_expiry_email.html', template_values)
                        send_mail(
                            '[SyllabusTracker] Fee expiry notification',
                            msg_plain,
                            None,
                            [template_values['email']],
                            html_message=msg_html,
                        )
                    else:
                        self.stdout.write("\t- "+fee_expiry.fee_definition.name + " expires on "+str(fee_expiry.fee_expiry_date))
import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from order.models import RFID  # Import the RFID model from your `order` app

class Command(BaseCommand):
    help = 'Import RFID data from a CSV file and store it in the database.'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='The path to the CSV file containing RFID data (RollNum, RFID)'
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        
        # Ensure the file exists
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        # Open and read the CSV file
        try:
            with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    rollnum = row.get('RollNum')
                    rfid_code = row.get('RFID')

                    if rollnum and rfid_code:
                        # Create or update RFID entry in the database
                        rfid, created = RFID.objects.get_or_create(
                            rollnum=rollnum,
                            defaults={'rfid_code': rfid_code}
                        )
                        if not created:
                            rfid.rfid_code = rfid_code  # Update the RFID code if it exists
                            rfid.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS(f"{'Created' if created else 'Updated'} RFID for RollNum: {rollnum}")
                        )
                    else:
                        self.stdout.write(self.style.WARNING("Row missing RollNum or RFID"))

            self.stdout.write(self.style.SUCCESS("RFID import completed successfully."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error processing file: {e}"))

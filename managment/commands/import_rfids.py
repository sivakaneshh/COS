from django.core.management.base import BaseCommand
from order.models import RFID  # Update with your actual model name
import pandas as pd

class Command(BaseCommand):
    help = 'Imports RFIDs from an Excel file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='The path to the Excel file containing RFID data')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        
        # Load the Excel file
        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reading Excel file: {e}"))
            return
        
        # Iterate through the DataFrame rows
        for _, row in df.iterrows():
            rollnum = row.get('RollNum')
            rfid_code = row.get('RFID')

            if rollnum and rfid_code:
                rfid, created = RFID.objects.get_or_create(rollnum=rollnum, defaults={'rfid_code': rfid_code})
                if not created:
                    rfid.rfid_code = rfid_code
                    rfid.save()
                self.stdout.write(self.style.SUCCESS(f"Processed RFID for RollNum: {rollnum}"))
            else:
                self.stdout.write(self.style.WARNING("Missing RollNum or RFID in row"))

        self.stdout.write(self.style.SUCCESS("RFID import completed successfully."))

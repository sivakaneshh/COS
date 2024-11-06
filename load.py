import os
import csv
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "canteen_ordering_sys.settings")
django.setup()

from order.models import RFID

def load_rfids(csv_path):
    # Check if the file exists
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return

    # Attempt to open and process the CSV
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        print("CSV file opened successfully.")
        
        for row in reader:
            try:
                # Verify and log row contents for debugging
                print(f"Processing row: {row}")
                
                # Attempt to create RFID entry in the database
                RFID.objects.create(
                    name=row['Name'],                 # Adjusted to match 'Name' column in CSV
                    roll_number=row['Rollnumber'],     # Adjusted to match 'Rollnumber' column in CSV
                    rfid_tag=int(row['RFID']),         # Adjusted to match 'RFID' column in CSV
                )
                
                print(f"Successfully imported RFID for roll number: {row['Rollnumber']}")
                
            except KeyError as e:
                print(f"Missing expected column in CSV file: {e}")
            except ValueError as e:
                print(f"Data type error with row {row}: {e}")
            except django.db.utils.IntegrityError as e:
                print(f"Database integrity error with row {row}: {e}")
            except Exception as e:
                print(f"Error importing RFID for row {row}: {e}")

if __name__ == "__main__":
    load_rfids("RFID_withname.csv")  # Ensure this is the correct path to your CSV file
    print("RFID data import complete!")

# coding=UTF-8

import Provider
import Validator
import csv
import datetime
import sys

# Set file I/O
INFILE = sys.argv[1]
OUTFILE = sys.argv[2]

sys.stdout.write("Opening files...\r")
infile = open(INFILE, "r")
outfile = open(OUTFILE, "w", newline='')
data = csv.DictReader(infile)
sys.stdout.flush()
sys.stdout.write("Opening files: DONE\n")

fieldnames = ["First Name", "Last Name", "CarePath ID", "NPI Number", "Mailing Street", "Mailing City", "Mailing State/Province", "Mailing Zip/Postal Code", "Validation Result"]
writer = csv.DictWriter(outfile,fieldnames)
writer.writeheader()

sys.stdout.write("Getting total rows...\r")
# Count total records in data
total_rows = 0
for row in data:
    total_rows += 1
infile.seek(0)
sys.stdout.flush()
sys.stdout.write(f"Getting total rows: {total_rows}\n")


# Initialize record counts
current_record = 0
valid_count = 0
not_valid_count = 0
err_count = 0

# Create validator object

logfile = f'{str(datetime.date.today()).replace("-","_")}.txt'
sys.stdout.write(f"Creating logfile logs/{logfile}...\r")
v = Validator.Validator(debug=True, logfile=f'logs/{logfile}')
sys.stdout.flush()
sys.stdout.write(f"Creating logfile logs/{logfile}: DONE\n")

try: 
    for line in data:
        if current_record == 0:
            current_record += 1
            continue
        provider = Provider.Provider(line["First Name"], line["Last Name"], line["CarePath ID"], line["NPI Number"], line["Mailing Street"], line["Mailing City"], line["Mailing Zip/Postal Code"], line["Mailing State/Province"])

        if provider.bad_npi:
            sys.stdout.write(f'Checking NPI registry - Progress: {str(current_record).zfill(len(str(total_rows)))}/{total_rows} ({(current_record/total_rows) * 100:.2f}%)\r')
            sys.stdout.flush()
        else:
            sys.stdout.write(f'Checking NPI registry - Progress: {str(current_record).zfill(len(str(total_rows)))}/{total_rows} ({(current_record/total_rows) * 100:.2f}%)\r')
            sys.stdout.flush()
        try:
            v.query_registry(provider.npi)
            if v.validation_error:
                sys.stdout.write(f'An error has occurred. Unable to validate. Skipping...\r')
                sys.stdout.flush()
                err_count += 1
                break
            if provider.bad_npi:
                not_valid_count += 1
            else:
                v.validate_npi(provider)
                v.validate_name(provider)
                v.push_validation_result(provider)
                if v.npi_valid and v.name_valid: # and v.address_valid:
                    valid_count += 1
                else:
                    not_valid_count += 1
        except ConnectionError as e:
            print(f'An error occurred. Connection Error: {e}')
        csv_row = {
            "First Name" : provider.fname, 
            "Last Name" : provider.lname, 
            "CarePath ID" : provider.carepath, 
            "NPI Number" : provider.npi, 
            "Mailing Street" : provider.street, 
            "Mailing City" : provider.city, 
            "Mailing State/Province" : provider.state, 
            "Mailing Zip/Postal Code" : provider.zipcode, 
            "Validation Result" : provider.validated
        }
        if csv_row["Validation Result"] == "Validated":
            writer.writerow(csv_row)
        current_record += 1

finally:
    print(f'\n{valid_count + not_valid_count} records checked.')
    if (valid_count + not_valid_count) > 0:
        print(f'{valid_count} records ({round(valid_count/(valid_count + not_valid_count) * 100, 2)}%) validated.')
    print(f'{err_count} records not checked.')

# File closing and cleanup
v.logfile.close()
infile.close()
outfile.close()
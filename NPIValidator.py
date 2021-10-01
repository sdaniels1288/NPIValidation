import Provider
import Validator
import csv
import datetime

# Set file I/O
infile = open("data/2021 09 27.csv", "r")
outfile = open("results/2021_09_27_results.csv", "w", newline='')
data = csv.DictReader(infile)

fieldnames = ["First Name", "Last Name", "CarePath ID", "NPI Number", "Mailing Street", "Mailing City", "Mailing State/Province", "Mailing Zip/Postal Code", "Validation Result"]
writer = csv.DictWriter(outfile,fieldnames)
writer.writeheader()

# Attempted to add an automatic total record count. - Future release
total_rows = 0
for row in data:
     total_rows += 1

infile.seek(0)

# Initialize record counts
current_record = 0
valid_count = 0
not_valid_count = 0
err_count = 0

logfile = f'{str(datetime.date.today()).replace("-","_")}.txt'
# Create validator object
v = Validator.Validator(debug=True, logfile=f'logs/{logfile}')

try: 
    for line in data:
        if current_record == 0:
            current_record += 1
            continue
        provider = Provider.Provider(line["First Name"], line["Last Name"], line["CarePath ID"], line["NPI Number"], line["Mailing Street"], line["Mailing City"], line["Mailing Zip/Postal Code"], line["Mailing State/Province"])

        if provider.npi == "0":
            print(f'Record {current_record}/{total_rows} ({round(current_record/total_rows * 100, 2)}%) - NPI {provider.npi} is invalid. Skipping query.')
        else:
            print(f'Record {current_record}/{total_rows} ({round(current_record/total_rows * 100, 2)}%) - Checking registry for NPI: {provider.npi}... ')
        #print(f"Record {current_record} of  {total_rows} - Checking registry for NPI: {provider.npi}...")
        try:
            v.query_registry(provider.npi)
            if v.validation_error:
                print(f'An error has occurred. Unable to validate. Skipping...')
                err_count += 1
                break
            v.validate_npi(provider)
            v.validate_name(provider)
            # v.validate_address(provider)
            v.push_validation_result(provider)
            if v.npi_valid and v.name_valid: # and v.address_valid:
                # print(f"[OK] Provider {provider.fname} {provider.lname} ({provider.carepath}) validated")
                valid_count += 1
            else:
                # print(f"[ERR] Provider {provider.fname} {provider.lname} ({provider.carepath}) not validated")
                not_valid_count += 1
        except ConnectionError as e:
            print(f'An error occurred. Connection Error: {e}')
        # print()
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

# except Exception as e:
#     print(e.__traceback__.tb_lineno, e.__traceback__.tb_lasti)

finally:
    print(f'{valid_count + not_valid_count} records checked.')
    if (valid_count + not_valid_count) > 0:
        print(f'{valid_count} records ({round(valid_count/(valid_count + not_valid_count) * 100, 2)}%) validated.')
    print(f'{err_count} records not checked.')

# File closing and cleanup
v.logfile.close()
infile.close()
outfile.close()
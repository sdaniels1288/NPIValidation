import csv
import Validator

class Provider:

    def __init__(self, fname, lname, carepath, npi, street, city, zipcode, state):
        self.fname = fname
        self.lname = lname
        self.carepath = carepath
        self.npi = npi
        self.street = street
        self.city = city
        self.zipcode = zipcode
        self.state = state
        self.validated = ""

    def show_provider(self):
        return f'Provider Name: {self.fname} {self.lname}, CarePath ID: {self.carepath}, NPI: {self.npi}, Address: {self.street} {self.city}, {self.state} {self.zipcode}'

        
if __name__ == "__main__":
    infile = open("NPI_validation.csv", "r")
    data = csv.DictReader(infile)
    valid_count = 0
    err_count = 0
    for i in range(250):
        line = data.__next__()
        #print(line)
        provider = Provider(line["First Name"], line["Last Name"], line["CarePath ID"], line["NPI Number"], line["Mailing Street"], line["Mailing City"], line["Mailing Zip/Postal Code"], line["Mailing State/Province"])
        v = Validator.Validator(debug=True)
        print(f"Checking registry for NPI: {provider.npi}...")
        v.query_registry(provider.npi)
        if v.validation_error:
            print(f'An error occurred. Unable to validate.\n')
            continue
        v.validate_npi(provider)
        v.validate_name(provider)
        v.validate_address(provider)
        if v.npi_valid and v.name_valid and v.address_valid:
            print(f"[OK] Provider {provider.fname} {provider.lname} ({provider.carepath}) validated")
            valid_count += 1
        else:
            print(f"[ERR] Provider {provider.fname} {provider.lname} ({provider.carepath}) not validated")
            err_count += 1
        print()
    
    print(f'{valid_count + err_count} records checked. {valid_count} records ({round(valid_count/(valid_count + err_count) * 100, 2)}%) validated.')

import requests
import json
from datetime import datetime

class Validator:

    api_URL = "https://npiregistry.cms.hhs.gov/api/?version=2.1"

    state_abbr = {
        "Alabama" : "AL", "Alaska" : "AK", "Arizona" : "AZ", "Arkansas" : "AR", "California" : "CA", "Colorado" : "CO", "Connecticut" : "CT", "Delaware" : "DE",
        "District of Columbia" : "DC", "Florida" : "FL", "Georgia" : "GA", "Guam" : "GU", "Hawaii" : "HI", "Idaho" : "ID", "Illinois" : "IL", "Indiana" : "IN",
        "Iowa" : "IA", "Kansas" : "KS", "Kentucky" : "KY", "Louisiana" : "LA", "Maine" : "ME", "Maryland" : "MD", "Massachusetts" : "MA", "Michigan" : "MI",
        "Minnesota" : "MN", "Mississippi" : "MS", "Missouri" : "MO", "Montana" : "MT", "Nebraska" : "NE", "Nevada" : "NV", "New Hampshire" : "NH", "New Jersey" : "NJ",
        "New Mexico" : "NM", "New York" : "NY", "North Carolina" : "NC", "North Dakota" : "ND", "Northern Mariana Islands" : "MP", "Ohio" : "OH", "Oklahoma" : "OK",
        "Oregon" : "OR", "Pennsylvania" : "PA", "Puerto Rico" : "PR", "Rhode Island" : "RI", "South Carolina" : "SC", "South Dakota" : "SD", "Tennessee" : "TN",
        "Texas" : "TX", "United States Minor Outlying Islands" : "UM", "US Virgin Islands" : "VI", "Utah" : "UT", "Vermont" : "VT", "Virginia" : "VA",
        "Washington" : "WA", "West Virginia" : "WV", "Wisconsin" : "WI", "Wyoming" : "WY", "" : ""
    }
    
    bad_npi = ["0", "9999999999"]

    def __init__(self, debug=False, logfile=""):
        self.npi_valid = False
        self.name_valid = False
        self.address_valid = False
        self.debug = debug
        if logfile:
            self.logfile = open(logfile, "w")
        self.validation_error = False

    def query_registry(self, npi):

        # Skip if known bad value
        if npi in self.bad_npi:
            self.npi_valid = False
            if self.debug:
                self.logfile.write(f"\n{datetime.now()} - NPI entry {npi} is invalid. Skipping query.")
        else:

            # API call to NPI registry
            url = self.api_URL + f'&number={npi}'
            
            try: 
                r = requests.get(url)
                self.response = json.loads(r.text)
                if self.debug:
                    self.logfile.write(f"\n{datetime.now()} - [{r.status_code}] - {url}\n")
                
            except ConnectionError as e:
                if self.debug:
                    self.logfile.write(f'\n{datetime.now()} - Connection Error\n')
                self.validation_error = True

            except Exception:
                if self.debug:
                    self.logfile.write(f'\n{datetime.now()} - Unspecified Exception')
                self.validation_error = True

    def validate_npi(self, provider):
    
        # Validate NPI
        try:
            self.result_count = self.response['result_count']

            # API call returns no result - NPI is correct length, but not matched
            if self.result_count == 0:
                if self.debug:
                    self.logfile.write(f"[ERR] API Response OK - {self.result_count} results found for {provider.npi}\n")
                self.npi_valid = False

            # API returns more than one result - A valid prescriber should have only one NPI
            elif self.result_count > 1:
                if self.debug:
                    self.logfile.write(f"[ERR] API Response OK - {self.result_count} results found for {provider.npi}\n")
                self.npi_valid = False

            # Confirm that NPI is Individual, not Organization
            else:
                if self.response["results"][0]["enumeration_type"] == "NPI-1":
                    if self.debug:
                        self.logfile.write(f"[OK] API Response OK - Individual NPI: {provider.npi} - Results: {self.result_count}\n")
                    self.npi_valid = True
                else:
                    if self.debug:
                        self.logfile.write(f"[ERR] API Response OK - Organization NPI: {provider.npi} - Results: {self.result_count}\n")
                    self.npi_valid = False
        
        # NPI requested is invalid format
        except KeyError:
            if self.debug:
                self.logfile.write(f"[ERR] Invalid NPI: {provider.npi}\n")
            self.npi_valid = False

    def validate_name(self, provider):

        # Only validate name if NPI search returns results
        if self.npi_valid == True:
            demographics = self.response["results"][0]['basic']

            # Confirm provider name matches
            if provider.fname.upper() == demographics['first_name'].upper() and provider.lname.upper() == demographics['last_name'].upper():
                if self.debug:
                    self.logfile.write(f'[OK] Provider Name: {provider.fname} {provider.lname} | Match: {demographics["first_name"]} {demographics["last_name"]}\n')
                self.name_valid = True
            else:
                if self.debug:
                    self.logfile.write(f'[ERR] Name mismatch: {provider.fname} {provider.lname} | Match: {demographics["first_name"]} {demographics["last_name"]}\n')
                self.name_valid = False

        # No search if NPI invalid
        else:
            self.name_valid = False
            if self.debug:
                self.logfile.write("[ERR] Name not checked. NPI invalid.\n")

    def validate_address(self, provider):

        # Only validate address if NPI search returns results
        if self.npi_valid == True:
            address_response = self.response["results"][0]["addresses"]
            practice_address = {
                "street" : "",
                "street2" : "",
                "city" : "",
                "state" : "",
                "zipcode" : "",
            }

            # Read primary practice address in to validator
            for address in address_response:
                if address["address_purpose"] == "LOCATION":
                    practice_address["street"] = address["address_1"]
                    practice_address["street2"] = address["address_2"]
                    practice_address["city"] = address["city"]
                    practice_address["state"] = address["state"]
                    practice_address["zipcode"] = address["postal_code"][:5]

            # Convert provider state into state code
            provider_statecode = self.state_abbr[provider.state]

            # Match Street Address
            if provider.street.upper().rstrip() == (practice_address["street"] + practice_address["street2"]).upper():
                if self.debug:
                    self.logfile.write(f'[OK] Street address match: {provider.street} | {practice_address["street"]} {practice_address["street2"]}\n')
                self.street_valid = True
            else:
                if self.debug:
                    self.logfile.write(f'[ERR] Street address mismatch: {provider.street} | {practice_address["street"]} {practice_address["street2"]}\n')
                self.street_valid = False

            # Match City
            if provider.city.upper().rstrip() == practice_address["city"].upper():
                if self.debug:
                    self.logfile.write(f'[OK] City match: {provider.city} | {practice_address["city"]}\n')
                self.city_valid = True
            else:
                if self.debug:
                    self.logfile.write(f'[ERR] City mismatch: {provider.city} | {practice_address["city"]}\n')
                self.city_valid = False

            # Match State
            if provider_statecode.upper() == practice_address["state"].upper():
                if self.debug:
                    self.logfile.write(f'[OK] State match: {provider.state} | {practice_address["state"]}\n')
                self.state_valid = True
            else:
                if self.debug:
                    self.logfile.write(f'[ERR] State mismatch: {provider.state} | {practice_address["state"]}\n')
                self.state_valid = False
            
            # Match ZIP
            if provider.zipcode.upper().rstrip() == practice_address["zipcode"].upper():
                if self.debug:
                    self.logfile.write(f'[OK] ZIP match: {provider.zipcode} | {practice_address["zipcode"]}\n')
                self.zip_valid = True
            else:
                if self.debug:
                    self.logfile.write(f'[ERR] ZIP mismatch: {provider.zipcode} | {practice_address["zipcode"]}\n')
                self.zip_valid = False

            if self.street_valid and self.city_valid and self.state_valid and self.zip_valid:
                if self.debug:
                    self.logfile.write(f'[OK] Address validated\n')
                self.address_valid = True
            else:
                if self.debug:
                    self.logfile.write(f'[ERR] Address not validated\n')
                self.address_valid = False
        
        else:
            if self.debug:
                self.logfile.write(f'[ERR] Address not checked. NPI invalid.\n')

    def push_validation_result(self, provider):
        if self.npi_valid == False:
            provider.validated = "NPI invalid"
        elif self.name_valid == False:
            provider.validated = "Name mismatch"
        # elif self.address_valid == False:
            # subtypes = []
            # if self.street_valid == False:
            #     subtypes.append("Street")
            # if self.city_valid == False:
            #     subtypes.append("City")
            # if self.state_valid == False:
            #     subtypes.append("State")
            # if self.zip_valid == False:
            #     subtypes.append("Zipcode")
            # provider.validated = f"Address mismatch - {', '.join(subtypes)}"

            #provider.validated = "Address mismatch"
        else:
            provider.validated = "Validated"


# provider = {
#     'First Name': 'Abdul', 
#     'Last Name': 'Halabi', 
#     'Mailing Street': '3325 POCAHONTAS RD', 
#     'Mailing City': 'BAKER CITY', 
#     'Mailing Zip/Postal Code': '97814', 
#     'Mailing State/Province': 'Oregon', 
#     'CarePath ID': 'PT-02314756', 
#     'NPI Number': '1043658412'
#     }
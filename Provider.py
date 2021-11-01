import Validator

class Provider:

    bad_npi = [
        "0",
        "9999999999"
    ]

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
        if npi in self.bad_npi:
            self.bad_npi = True
        else:
            self.bad_npi = False

    def show_provider(self):
        return f'Provider Name: {self.fname} {self.lname}, CarePath ID: {self.carepath}, NPI: {self.npi}, Address: {self.street} {self.city}, {self.state} {self.zipcode}'
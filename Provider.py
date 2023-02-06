import Validator

class Provider:

    bad_npi = [
        "0",
        "9999999999"
    ]

    def __init__(self, fname, lname,  npi):
        self.fname = fname
        self.lname = lname
        self.npi = npi
        self.validated = ""
        if npi in self.bad_npi:
            self.bad_npi = True
        else:
            self.bad_npi = False

    def show_provider(self):
        return f'Provider Name: {self.fname} {self.lname}, NPI: {self.npi}, Address: {self.street} {self.city}, {self.state} {self.zipcode}'
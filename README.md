# NPI Validator

This command line application takes a CSV file of provider names and National Provider Identifiers (NPIs), and checks them against the [NPPES NPI Registry](https://npiregistry.cms.hhs.gov/search). It then returns the validated NPIs as a CSV file. The output can have one of three statuses:

- **Valid** - NPI number is valid, and the name matches the registry
- **Bad NPI** - The NPI number is either incorrectly formatted, dummy data, or does not return a result from the API.
- **Name Mismatch** - The NPI number is valid, and returns a match from the database, but the name passed to the validator does not match the registered provider name.

## Usage

```python NPIValidator.py input_file.csv [output_file.csv]```

The application requires an input file be passed when calling the application. An output file is optional. If not supplied, the application will create a fallback output file with the format ```{year}_{month}_{day}_result.csv```.
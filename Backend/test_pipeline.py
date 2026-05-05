from Pipeline.agent import run_pipeline

sample = [
    {
        "npi": "1234567890",
        "provider_first_name": "JOHN",
        "provider_last_name_(legal_name)": "DOE",
        "provider_first_line_business_practice_location_address": "NY"
    }
]

print(run_pipeline(sample))
import pandas as pd
import requests
import re


def norm(s):
    s = str(s).upper().strip()
    s = re.sub(r'[^A-Z0-9 ]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s

# AGENT 1 — DATA VALIDATION

def data_validation_agent(row):
    npi = str(row.get("npi", "")).strip()

    return {
        "npi_format_valid": len(npi) == 10 and npi.isdigit()
    }

# AGENT 2 — NPI VALIDATION

def npi_validation_agent(npi):
    if len(npi) != 10 or not npi.isdigit():
        return None, "INVALID_FORMAT"

    url = f"https://npiregistry.cms.hhs.gov/api/?number={npi}&version=2.1"

    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()

        if data.get("result_count", 0) != 1:
            return None, "NOT_FOUND"

        return data["results"][0], "ACTIVE"

    except:
        return None, "API_ERROR"

# AGENT 3 — DATA SOURCE ENRICHMENT

def data_source_enrichment_agent(api_data):
    if not api_data:
        return {
            "full_name": "Not Found",
            "address": "Not Found",
            "taxonomy": "Not Found",
            "enumeration_date": "Not Found"
        }

    basic = api_data.get("basic", {})
    addresses = api_data.get("addresses", [])
    taxonomies = api_data.get("taxonomies", [])

    return {
        "full_name": f"{basic.get('first_name','')} {basic.get('last_name','')}".strip(),
        "address": addresses[0].get("address_1", "") if addresses else "N/A",
        "taxonomy": taxonomies[0].get("desc", "") if taxonomies else "N/A",
        "enumeration_date": basic.get("enumeration_date", "N/A")
    }

# AGENT 4 — DIRECTORY MANAGEMENT

def directory_management_agent(row, enriched):
    csv_name = norm(f"{row.get('provider_first_name','')} {row.get('provider_last_name','')}")
    npi_name = norm(enriched.get("full_name", ""))

    return {
        "name_match": csv_name == npi_name
    }

# AGENT 5 — QUALITY ASSURANCE

def quality_assurance_agent(validation, npi_valid, matches):
    score = 0.0

    if validation["npi_format_valid"]:
        score += 0.2

    if npi_valid:
        score += 0.4

    if matches["name_match"]:
        score += 0.4
    else:
        score -= 0.3

    score = max(0, min(score, 1))
    return round(score, 2)

# AGENT 6 — MASTER ORCHESTRATOR

def master_orchestrator_agent(input_data):
    df = pd.DataFrame(input_data).fillna("")
    results = []

    for _, row in df.iterrows():
        row = row.to_dict()

        validation = data_validation_agent(row)

        api_data, npi_status = npi_validation_agent(row.get("npi", ""))
        npi_valid = api_data is not None

        enriched = data_source_enrichment_agent(api_data)

        matches = directory_management_agent(row, enriched)

        score = quality_assurance_agent(validation, npi_valid, matches)

        if score >= 0.8:
            status = "AUTO_ACCEPT"
        elif score >= 0.5:
            status = "REVIEW"
        else:
            status = "REJECT"

        results.append({
            "confidence": score,
            "status": status,
            "npi_status": npi_status,
            "name_match": matches["name_match"],
            "details": enriched
        })

    return results


def run_pipeline(input_data):
    return master_orchestrator_agent(input_data)
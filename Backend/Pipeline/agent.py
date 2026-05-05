import pandas as pd
import requests

def norm(s):
    return " ".join(str(s).upper().split())


# ===============================
# AGENT 1 — VALIDATION
# ===============================
def data_validation_agent(row):
    npi = str(row.get("npi", "")).strip()
    addr = str(row.get("provider_address", "")).strip()

    return {
        "npi_format_valid": len(npi) == 10 and npi.isdigit(),
        "address_present": len(addr) > 5,
    }


# ===============================
# EMPTY RESPONSE
# ===============================
def _empty_response(status):
    return {
        "npi_valid": False,
        "npi_status": status,
        "name_match": False,
        "address_match": False,
        "npi_data": {
            "full_name": "Not Found",
            "address": "Not Found",
            "taxonomy": "Not Found",
            "enumeration_date": "Not Found",
        }
    }


# ===============================
# AGENT 2 — NPI VALIDATION
# ===============================
def npi_validation_agent(row):
    npi = str(row.get("npi", "")).strip()

    if len(npi) != 10 or not npi.isdigit():
        return _empty_response("INVALID_FORMAT")

    url = f"https://npiregistry.cms.hhs.gov/api/?number={npi}&version=2.1"

    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()

        if data.get("result_count", 0) != 1:
            return _empty_response("NOT_FOUND")

        rec = data["results"][0]
        basic = rec.get("basic", {})
        addresses = rec.get("addresses", [])
        taxonomies = rec.get("taxonomies", [])

        # Extract data
        npi_first = basic.get("first_name", "")
        npi_last = basic.get("last_name", "")
        full_name = f"{npi_first} {npi_last}".strip()

        address = addresses[0].get("address_1", "") if addresses else ""
        taxonomy = taxonomies[0].get("desc", "") if taxonomies else ""

        # Matching
        csv_first = str(row.get("provider_first_name", "")).strip()
        csv_last = str(row.get("provider_last_name", "")).strip()

        csv_full = norm(f"{csv_first} {csv_last}")
        npi_full = norm(full_name)

        name_match = (
            csv_full != "" and npi_full != "" and (
                csv_full == npi_full or
                csv_full in npi_full or
                npi_full in csv_full
            )
        )

        csv_addr = norm(row.get("provider_address", ""))
        npi_addr = norm(address)

        address_match = (
            csv_addr != "" and npi_addr != "" and (
                csv_addr == npi_addr or
                csv_addr in npi_addr or
                npi_addr in csv_addr
            )
        )

        return {
            "npi_valid": True,
            "npi_status": "ACTIVE",
            "name_match": name_match,
            "address_match": address_match,
            "npi_data": {
                "full_name": full_name if full_name else "N/A",
                "address": address if address else "N/A",
                "taxonomy": taxonomy if taxonomy else "N/A",
                "enumeration_date": basic.get("enumeration_date", "N/A"),
            }
        }

    except:
        return _empty_response("API_ERROR")


# ===============================
# SCORING (ORIGINAL)
# ===============================
def quality_assurance_agent(v1, v2):
    score = 0.0

    if v1.get("npi_format_valid"):
        score += 0.1
    if v1.get("address_present"):
        score += 0.1
    if v2.get("npi_valid"):
        score += 0.4
    if v2.get("name_match"):
        score += 0.3
    if v2.get("address_match"):
        score += 0.1

    if score >= 0.8:
        status = "AUTO_ACCEPT"
    elif score >= 0.5:
        status = "REVIEW"
    else:
        status = "REJECT"

    return {"confidence": round(score, 2), "status": status}


# ===============================
# MAIN PIPELINE
# ===============================
def run_pipeline(input_data):
    df = pd.DataFrame(input_data).fillna("")
    results = []

    for _, row in df.iterrows():
        row = row.to_dict()

        v1 = data_validation_agent(row)
        v2 = npi_validation_agent(row)
        v3 = quality_assurance_agent(v1, v2)

        results.append({
            "confidence": v3["confidence"],
            "status": v3["status"],
            "npi_status": v2["npi_status"],
            "details": v2["npi_data"]
        })

    return results
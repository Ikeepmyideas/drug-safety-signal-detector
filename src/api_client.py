import json
import logging
from typing import Any, Dict, List, Optional
import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

OPENFDA_BASE_URL = "https://api.fda.gov/drug/event.json"

def fetch_events(
        drug_name: str,
        limit: int = 100,
        api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch adverse druf event reports for a given active substance.

    param drug_name: Active substance or medicinal product name (e.g., 'METFORMIN').
    param limit: Number of event reports to retrieve (max 100 per single query).
    param api_key: Optional openFDA API key to unlock higher rate limits.
    return: List of raw safety report dictionaries.
    """
    cleaned_drug = drug_name.strip().upper()
    if not cleaned_drug:
        raise ValueError("Drug name must not be empty.")

    # Restrict limit to openFDA standart bounds
    capped_limit = min(max(limit,1),100)

    # Search query targeting the medecinal product field
    params = {
        "search": f'patient.drug.medicinalproduct:"{cleaned_drug}"',
        "limit": capped_limit,
    }

    if api_key:
        params["api_key"] = api_key

    headers = {
        "User-Agent": "DrugSafetySignalDetector/1.0 (Portfolio Project; Academic Use)",
        "Accept": "application/json",
    }

    try:
        # Enforce a 10 second timeout to prevent hung worker threads
        response = requests.get(
            OPENFDA_BASE_URL,
            params=params,
            headers=headers,
            timeout=10,
        )

        # HTTP 404 indicates zero matching records for the search query
        if response.status_code == 404:
            logger.warning("No adverse event reports found for drug: %s", cleaned_drug)
            return []

        # Raise an exception for unexpected 4xx (client) or 5xx (server) errors
        response.raise_for_status()

        payload = response.json()
        results = payload.get("results", [])
        logger.info("Successfully fetched %d records for '%s'.", len(results), cleaned_drug)
        return results

    except requests.exceptions.Timeout:
        logger.error("Request timed out while connecting to openFDA. ")
        return []
    except requests.exceptions.RequestException as err:
        logger.error("Network or HTTP error communicating with openFDA: %s", err)
        return []


if __name__ == "__main__":
    # Local integration test inspecting patient.frug and patient.reaction fields
    target_drug = "SPIRONOLACTONE"
    print(f"--- Querying openFDA for: {target_drug} ---\n")

    events = fetch_events(drug_name=target_drug, limit=2)

    if events:
        first_event = events[0]
        patient_data = first_event.get("patient", {})

        print(" Safety Report Overview:")
        print(f" Safety Report ID: {first_event.get('safetyreportid', 'N/A')}")
        print(f" Receive Date: {first_event.get('receivedate', 'N/A')}")

        # 1. Inspect 'patient.drug'
        drugs = patient_data.get("drug", [])
        print(f"/n Reported Drugs ({len(drugs)})")
        for drug in drugs[:3]:
            product = drug.get("medicinalproduct", "Unknown")
            role_code = drug.get("drugcharacterization", "Unspecified")
            print(f"  - Product: {product} (Role code: {role_code})")


        # 2. Inspect 'patient.reaction'
        reactions = patient_data.get("reaction", [])
        print(f"/n Reported Adverse Reactions ({len(reactions)}):")
        for reaction in reactions[:5]:
            pt_term = reaction.get("reactionmeddrapt", "Unknown")
            outcome = reaction.get("reactionoutcome", "Unspecified")
            print(f"  - MedDRA PT: {pt_term} (Outcome code: {outcome})")
    else:
        print(" Failed to retrieve records.")
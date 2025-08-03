import os
import requests
from dotenv import load_dotenv

load_dotenv()
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")

def enrich_company_hunter(domain):
    url = "https://api.hunter.io/v2/companies/find"
    params = {
        "domain": domain,
        "api_key": HUNTER_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if response.status_code != 200 or "data" not in data:
            return {"Domain": domain, "Enrichment Status": "Not Found"}

        d = data["data"]
        return {
            "Domain": domain,
            "Company": d.get("name"),
            "Industry": d.get("category", {}).get("industry"),
            "Sector": d.get("category", {}).get("sector"),
            "Size": d.get("metrics", {}).get("employees"),
            "Founded": d.get("foundedYear"),
            "Location": d.get("location"),
            "LinkedIn": f"https://linkedin.com/{d.get('linkedin', {}).get('handle')}" if d.get("linkedin") else None,
            "Logo": d.get("logo"),
            "Relevance Score": sum([
                1 if d.get("category", {}).get("industry") else 0,
                1 if d.get("metrics", {}).get("employees") else 0,
                1 if d.get("linkedin", {}).get("handle") else 0,
            ])
        }

    except Exception as e:
        print(f"[ERROR] Company enrichment failed for {domain}: {e}")
        return {"Domain": domain, "Enrichment Status": "Error"}

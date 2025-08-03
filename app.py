from flask import Flask, render_template, request
import pandas as pd
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")

app = Flask(__name__)

def compute_relevance_score(d):
    score = 0
    score += bool(d.get("name"))
    score += bool(d.get("category", {}).get("sector"))
    score += bool(d.get("category", {}).get("industry"))
    score += bool(d.get("metrics", {}).get("employees"))
    score += bool(d.get("foundedYear"))
    score += bool(d.get("location"))
    score += bool(d.get("linkedin", {}).get("handle"))
    score += bool(d.get("logo"))
    score += bool(d.get("description"))
    score += bool(d.get("tags"))
    score += bool(d.get("tech"))
    return score

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
        relevance_score = compute_relevance_score(d)

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
            "Description": d.get("description"),
            "Tags": ", ".join(d.get("tags", [])) if d.get("tags") else None,
            "Technologies": ", ".join(d.get("tech", [])) if d.get("tech") else None,
            "Relevance Score": relevance_score
        }

    except Exception as e:
        print(f"[ERROR] Company enrichment failed for {domain}: {e}")
        return {"Domain": domain, "Enrichment Status": "Error"}

def enrich_data(df):
    enriched = []
    for _, row in df.iterrows():
        domain = row["Website"].replace("https://", "").replace("http://", "").replace("www.", "").strip("/")
        enriched_data = enrich_company_hunter(domain)
        enriched.append({**row, **enriched_data})
    return pd.DataFrame(enriched)

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    error = None

    if request.method == "POST":
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            df = pd.read_csv(file)
            enriched_df = enrich_data(df)
            results = enriched_df.to_dict(orient="records")

        elif 'domain' in request.form and request.form['domain'].strip() != '':
            domain = request.form['domain'].strip()
            df = pd.DataFrame([{"Website": domain}])
            enriched_df = enrich_data(df)
            results = enriched_df.to_dict(orient="records")

        else:
            error = "Please upload a CSV file or enter a domain."

    return render_template("index.html", results=results, error=error)

if __name__ == "__main__":
    app.run(debug=True)

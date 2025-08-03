# main.py

import pandas as pd
from enrichment import enrich_data
from scoring import calculate_score

def main():
    df = pd.read_csv("data/sample_companies.csv")
    enriched_df = enrich_data(df)

    # Optional scoring — modify as needed
    enriched_df["Relevance Score"] = enriched_df["Emails Found"] + enriched_df["Pattern"].notnull().astype(int)
    enriched_df["LinkedIn"] = enriched_df["LinkedIn"].fillna("Not found")

    enriched_df = enriched_df.sort_values(by="Relevance Score", ascending=False)
    print(enriched_df)

    enriched_df.to_csv("output/enriched_companies.csv", index=False)
    print("\nSaved to output/enriched_companies.csv")

if __name__ == "__main__":
    main()

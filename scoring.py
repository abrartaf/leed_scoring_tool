import pandas as pd

def calculate_score(row):
    score = 0
    score += row["Emails Found"]
    if pd.notnull(row["Pattern"]):
        score += 1
    if row["LinkedIn"] != "Not found":
        score += 1
    if row["Industry"] == "SaaS":
        score += 3
    if isinstance(row["Employees"], int) and row["Employees"] <= 200:
        score += 2
    if row["AI-related"] == "Yes":
        score += 2
    return score

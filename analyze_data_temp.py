import pandas as pd

# Charger les données
csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTN1Jwosf-2KEvw6HSBx4s01S24_Tzy9SM38LoGaHUrGc-cSn0vf19ugAiNnA_6InNBQxBnyI7JN3wa/pub?gid=0&single=true&output=csv"

try:
    df = pd.read_csv(csv_url)

    print("=" * 80)
    print("COLONNES DISPONIBLES:")
    print("=" * 80)
    for i, col in enumerate(df.columns, 1):
        print(f"{i}. {col}")

    print("\n" + "=" * 80)
    print("APERÇU DES DONNÉES (5 premières lignes):")
    print("=" * 80)
    print(df.head())

    print("\n" + "=" * 80)
    print("VALEURS UNIQUES PAR COLONNE IMPORTANTE:")
    print("=" * 80)

    if "LA PLATEFORME" in df.columns:
        print("\n📌 LA PLATEFORME:")
        print(df["LA PLATEFORME"].value_counts())

    if "ETAT DE LA DEMANDE" in df.columns:
        print("\n📌 ETAT DE LA DEMANDE:")
        print(df["ETAT DE LA DEMANDE"].value_counts())

    if "CENTRE FISCAL" in df.columns:
        print("\n📌 TOP 10 CENTRES FISCAUX:")
        print(df["CENTRE FISCAL"].value_counts().head(10))

    if "OBJET" in df.columns:
        print("\n📌 ÉCHANTILLON OBJETS (10 premiers):")
        print(df["OBJET"].dropna().head(10).tolist())

    print("\n" + "=" * 80)
    print(f"TOTAL LIGNES: {len(df)}")
    print("=" * 80)

except Exception as e:
    print(f"❌ Erreur: {e}")

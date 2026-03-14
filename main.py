import pandas as pd
from pathlib import Path
import os
from medication_rules import analyze_patient_record, detect_medication_error

print("=" * 60)
print("Système de Détection d'Erreurs Médicamenteuses")
print("=" * 60)
print(f"Répertoire courant : {os.getcwd()}\n")

# Charger les données
try:
    medical_data = pd.read_csv("TEST.csv")
    print(f"✓ Fichier TEST.csv chargé avec succès")
    print(f"  - {len(medical_data)} lignes")
    print(f"  - {medical_data['ID'].nunique()} patient(s)\n")
except FileNotFoundError:
    print("✗ Erreur : TEST.csv non trouvé")
    exit(1)

# Analyser chaque patient
print("ANALYSE DES ERREURS MÉDICAMENTEUSES")
print("-" * 60)

all_errors = []
for patient_id in sorted(medical_data["ID"].unique()):
    patient_df = medical_data[medical_data["ID"] == patient_id].reset_index(drop=True)
    errors = analyze_patient_record(patient_df)
    
    print(f"\nPatient ID: {patient_id}")
    if errors:
        print(f"  ⚠️  {len(errors)} erreur(s) détectée(s):")
        for error in errors:
            severity_icon = "🚨" if error["severity"] == "danger" else "⚠️"
            print(f"     {severity_icon} [{error['time']}] {error['medication']}: {error['explanation']}")
            all_errors.append(error)
    else:
        print(f"  ✓ Aucune erreur détectée")

print("\n" + "=" * 60)
print(f"TOTAL : {len(all_errors)} erreur(s) détectée(s)")
print("=" * 60)
print("\n💡 Pour une interface graphique, exécutez:")
print("   streamlit run app.py")

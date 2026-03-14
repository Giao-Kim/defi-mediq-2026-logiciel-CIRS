"""
Interface Streamlit pour l'analyse des erreurs médicamenteuses
Option 2 - Présentation intégrée
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import os
from medication_rules import detect_medication_error, analyze_patient_record

st.set_page_config(
    page_title="Détecteur d'Erreurs Médicamenteuses",
    page_icon="⚕️",
    layout="wide"
)

st.title("⚕️ Système de Détection d'Erreurs Médicamenteuses")
st.markdown("Analyse en temps réel des admissions de médicaments pour patients en état de choc")

# Sidebar pour télécharger ou sélectionner le fichier
st.sidebar.header("📁 Chargement des données")

uploaded_file = st.sidebar.file_uploader("Télécharger CSV", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    # Chercher TEST.csv en local
    csv_path = Path("TEST.csv")
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        st.info(f"✓ Fichier TEST.csv chargé")
    else:
        st.warning("Aucun fichier CSV trouvé. Veuillez télécharger un fichier.")
        st.stop()

# Afficher stats générales
col1, col2, col3 = st.columns(3)
patients = df["ID"].nunique()
medications = len(df)
with col1:
    st.metric("Patients", patients)
with col2:
    st.metric("Administrations", medications)
with col3:
    st.metric("Médicaments uniques", df["Médicament"].nunique())

st.markdown("---")

# Onglets
tab1, tab2, tab3 = st.tabs(["📊 Vue d'ensemble", "🔍 Analyse détaillée", "📋 Données brutes"])

with tab1:
    st.subheader("Résumé des erreurs détectées")
    
    # Analyser tous les patients
    all_errors = []
    for patient_id in sorted(df["ID"].unique()):
        patient_df = df[df["ID"] == patient_id].reset_index(drop=True)
        errors = analyze_patient_record(patient_df)
        for error in errors:
            error["patient_id"] = patient_id
        all_errors.extend(errors)
    
    if all_errors:
        st.error(f"⚠️ {len(all_errors)} erreur(s) détectée(s)")
        
        # Tableau des erreurs
        error_data = []
        for error in all_errors:
            error_data.append({
                "Patient": error["patient_id"],
                "Heure": error["time"],
                "Médicament": error["medication"],
                "Type": error["error_type"],
                "Sévérité": error["severity"],
                "Description": error["explanation"]
            })
        
        error_df = pd.DataFrame(error_data)
        
        # Colorier selon la sévérité
        def style_severity(val):
            if val == "danger":
                return "background-color: #ff4d4d; color: white; font-weight: bold"
            elif val == "attention":
                return "background-color: #ffa500; color: white; font-weight: bold"
            else:
                return ""
        
        st.dataframe(
            error_df.style.applymap(style_severity, subset=["Sévérité"]),
            use_container_width=True
        )
    else:
        st.success("✓ Aucune erreur détectée")

with tab2:
    st.subheader("Analyse ligne par ligne")
    
    # Sélectionner patient
    patient_ids = sorted(df["ID"].unique())
    selected_patient = st.selectbox("Sélectionner un patient", patient_ids, key="patient_select")
    
    patient_df = df[df["ID"] == selected_patient].reset_index(drop=True)
    
    st.write(f"**Patient ID:** {selected_patient}")
    st.write(f"**Nombre d'administrations:** {len(patient_df)}")
    
    # Afficher chaque administration
    for idx, row in patient_df.iterrows():
        # Détection d'erreur en avance pour colorier l'expander
        error = detect_medication_error(row)
        
        # Déterminer l'icône et la couleur selon la sévérité
        if error["has_error"]:
            if error["severity"] == "danger":
                icon = "🚨"
            else:
                icon = "⚠️"
        else:
            icon = "✅"
        
        with st.expander(f"{icon} {row['Heure']} - {row['Médicament']} ({row['Dose (ml)']}ml)"):
            # Détails de l'administration
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("**Médicament**")
                st.write(row["Médicament"])
            with col2:
                st.write("**Dose**")
                st.write(f"{row['Dose (ml)']} ml")
            with col3:
                st.write("**Concentration**")
                st.write(f"{row['Concentration (mg/mL)']} mg/mL")
            
            st.divider()
            
            # Signes vitaux
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("FC", f"{row['FC']} bpm")
            with col2:
                st.metric("TA", f"{row['TA (Sys)']}/{row['TA (Dia)']} mmHg")
            with col3:
                st.metric("FR", f"{row['FR']} /min")
            with col4:
                st.metric("SAT", f"{row.get('SAT', 'N/A')}%")
            
            st.divider()
            
            # Détection d'erreur
            if error["has_error"]:
                if error["severity"] == "danger":
                    st.error(f"🚨 ERREUR DÉTECTÉE: {error['explanation']}")
                else:
                    st.warning(f"⚠️ ATTENTION: {error['explanation']}")
            else:
                st.success("✓ Pas d'erreur détectée")

with tab3:
    st.subheader("Données brutes")
    st.dataframe(df, use_container_width=True)
    
    # Télécharger comme CSV
    csv = df.to_csv(index=False)
    st.download_button(
        label="Télécharger données",
        data=csv,
        file_name="export.csv",
        mime="text/csv"
    )

st.markdown("---")
st.markdown("""
### 📋 Légende des erreurs
- **dose_inappropriée** : Dose en dehors de la plage recommandée
- **contrainte_vitale** : Signes vitaux incompatibles avec le médicament
- **concentration_inappropriée** : Concentration du médicament incorrecte
- **Sévérité 🚨 danger** : Erreur critique pouvant causer du tort au patient
- **Sévérité ⚠️ attention** : Erreur à vérifier avant administration
""")

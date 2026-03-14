"""
Règles de détection d'erreurs médicamenteuses
Basé sur les protocoles d'état de choc et les directives ACLS
"""

# Dosages appropriés par médicament et contexte
MEDICATION_RULES = {
    "Adénosine": {
        "normal_dose_range": (6, 12),  # mg
        "max_concentration": 3.0,  # mg/mL
        "administration_way": "Bolus",
    },
    "Amiodarone": {
        "normal_dose_range": (150, 450),  # mg
        "max_concentration": 50.0,  # mg/mL
        "administration_way": "Bolus, Perfusion",
    },
    "Ativan": {
        "normal_dose_range": (0.5, 4),  # mg
        "max_concentration": 2.0,  # mg/mL
        "administration_way": "Bolus, IM",
    },
    "Atropine": {
        "normal_dose_range": (0.5, 3),  # mg
        "max_concentration": 0.1,  # mg/mL
        "administration_way": "Bolus",
    },
    "Bicarbonate de sodium": {
        "normal_dose_range": (50, 100),  # mg
        "max_concentration": 1.0,  # mg/mL
        "administration_way": "Bolus",
    },
    "Chlorure de calcium": {
        "normal_dose_range": (500, 2000),  # mg
        "max_concentration": 100.0,  # mg/mL
        "administration_way": "Bolus",
    },
    "Dextrose": {
        "normal_dose_range": (12500, 50000),  # mg
        "max_concentration": 500.0,  # mg/mL
        "administration_way": "Bolus",
    },
    "Diltiazem": {
        "normal_dose_range": (10, 25),  # mg
        "max_concentration": 5.0,  # mg/mL
        "administration_way": "Bolus",
    },
    "Épinéphrine": {
        "normal_dose_range": (1.0, 1.0),  # mg en bolus IM
        "max_concentration": 0.1,  # mg/mL
        "administration_way": "IM, Bolus",
    },
    "Fentanyl": {
        "normal_dose_range": (0.025, 0.1),  # mg
        "max_concentration": 0.05,  # mg/mL
        "administration_way": "Bolus",
    },
    "Insuline": {
        "normal_dose_range": (1.0, 1.0),  # mg
        "max_concentration": 100.0,  # mg/mL
        "administration_way": "Bolus",
    },
    "Naloxone": {
        "normal_dose_range": (0.1, 0.4),  # mg
        "max_concentration": 0.4,  # mg/mL
        "administration_way": "Bolus, IM",
    },
    "Norépinéphrine": {
        "normal_dose_range": (0.008, 0.032),  # mg
        "max_concentration": 0.016,  # mg/mL
        "administration_way": "Perfusion",
    },
    "Phényléphrine": {
        "normal_dose_range": (0.05, 0.20),  # mg
        "max_concentration": 0.10,  # mg/mL
        "administration_way": "Bolus",
    },
    "Propofol": {
        "normal_dose_range": (70, 175),  # mg
        "max_concentration": 10.0,  # mg/mL
        "administration_way": "Bolus",
    },
    "Rocuronium": {
        "normal_dose_range": (42, 84),  # mg
        "max_concentration": 10.0,  # mg/mL
        "administration_way": "Bolus",
    },
    "Soluté physiologique": {
        "normal_dose_range": (250, 2000),  # mg
        "max_concentration": 1.0,  # mg/mL
        "administration_way": "Perfusion",
    },
    "Sulfate de magnésium": {
        "normal_dose_range": (1000, 4000),  # mg
        "max_concentration": 500.0,  # mg/mL
        "administration_way": "Bolus",
    },
}

def detect_medication_error(row):
    """
    Détecte si une ligne contient une erreur médicamenteuse
    Retourne dict avec: has_error (bool), error_type (str), severity (str), explanation (str)
    """
    medication = row.get("Médicament", "").strip()
    dose = row.get("Dose (ml)", 0)
    concentration = row.get("Concentration (mg/mL)", 0)
    admin_route = row.get("Administration", "").strip()

    FC = row.get("FC", 0)
    TA_sys = row.get("TA (Sys)", 0)
    TA_dia = row.get("TA (Dia)", 0)
    SAT = row.get("SAT (O2)", 0)

    result = {
        "has_error": False,
        "error_type": None,
        "severity": "normal",
        "explanation": "",
    }

    if medication not in MEDICATION_RULES:
        return result

    rules = MEDICATION_RULES[medication]

    expected_admin_way = rules.get("administration_way", "").lower()
    actual_admin_route = admin_route.lower()

    expected_ways = [way.strip() for way in expected_admin_way.split(",")]

    if actual_admin_route not in expected_ways:
        result["has_error"] = True
        result["error_type"] = "administration_inappropriée"
        result["severity"] = "danger"
        result["explanation"] = (
            f"{medication}: Voie d'administration '{admin_route}' incorrecte. Attendu: {rules.get('administration_way')}"
        )
        return result

    if admin_route.lower() == "perfusion":
        return result

   
    min_dose, max_dose = rules.get("normal_dose_range", (0, 1000))
    
    concentration_dose = dose * concentration  # Dose totale en mg
    if concentration_dose < min_dose or concentration_dose > max_dose:
        result["has_error"] = True
        result["error_type"] = "dose_inappropriée"

        if concentration_dose * 1.1 < min_dose:
            dose_status = "trop bas"
            result["severity"] = "attention"
        elif concentration_dose > max_dose * 1.1:
            dose_status = "trop haut"
            result["severity"] = "danger"
        else:
            dose_status = "hors normes"
            result["severity"] = "attention"
        
        result["explanation"] = (
            f"{medication}: Dose {concentration_dose:.3g} mg ({min_dose}-{max_dose} mg) {dose_status}"
        )
        return result

    return result


def analyze_patient_record(df):
    """
    Analyse un enregistrement patient complet (toutes les lignes avec même ID)
    Retourne liste des erreurs détectées
    """
    errors = []
    medication_admin_ways = {}

    for idx, row in df.iterrows():
        medication = row.get("Médicament", "").strip()
        current_admin_way = row.get("Administration", "").strip().lower()

        if medication in medication_admin_ways:
            # Comparer avec la PREMIÈRE voie d'administration du médicament
            first_admin_way = medication_admin_ways[medication]
            if first_admin_way != current_admin_way:
                errors.append(
                    {
                        "has_error": True,
                        "error_type": "changement_voie_administration",
                        "severity": "danger",
                        "explanation": f"{medication}: Voie d'administration changée de {first_admin_way.upper()} à {row.get('Administration', '').strip()}",
                        "row_number": idx + 2,
                        "medication": medication,
                        "time": row.get("Heure", "?"),
                    }
                )
        else:
            # Enregistrer la PREMIÈRE voie d'administration pour ce médicament
            medication_admin_ways[medication] = current_admin_way

        error = detect_medication_error(row)
        if error["has_error"]:
            error["row_number"] = idx + 2  # +2 car en-tête + índex 0
            error["medication"] = row["Médicament"]
            error["time"] = row.get("Heure", "?")
            errors.append(error)

    return errors

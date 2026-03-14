"""
Règles de détection d'erreurs médicamenteuses
Basé sur les protocoles d'état de choc et les directives ACLS
"""

# Dosages appropriés par médicament et contexte
MEDICATION_RULES = {
    "Épinéphrine": {
        "normal_dose_range": (0.3, 1.0),  # mg en bolus IM
        "max_concentration": 1.0,  # mg/mL
        "vitals_constraints": {
            "FC_min": 40,  # Ne pas donner si FC < 40
            "FC_max": 200,  # Attention si FC > 200
            "TA_sys_min": 60,  # Ne pas donner si TAS < 60
        }
    },
    "Norépinéphrine": {
        "normal_dose_range": (0.5, 2.0),
        "max_concentration": 1.0,
        "vitals_constraints": {"FC_min": 40}
    },
    "Atropine": {
        "normal_dose_range": (0.5, 1.0),
        "max_concentration": 0.5,
        "vitals_constraints": {"FC_min": 30}  # Pour bradycardie
    },
    "Amiodarone": {
        "normal_dose_range": (150, 300),
        "max_concentration": 50.0,
        "vitals_constraints": {"FC_min": 0}
    },
    "Dextrose": {
        "normal_dose_range": (10, 50),
        "max_concentration": 500.0,
        "vitals_constraints": {}
    },
    "Insuline": {
        "normal_dose_range": (0.1, 5),
        "max_concentration": 100.0,
        "vitals_constraints": {}
    },
    "Fentanyl": {
        "normal_dose_range": (0.5, 2.0),
        "max_concentration": 50.0,
        "vitals_constraints": {"FC_min": 40}
    },
    "Propofol": {
        "normal_dose_range": (1, 2.5),
        "max_concentration": 10.0,
        "vitals_constraints": {}
    },
    "Rocuronium": {
        "normal_dose_range": (1.2, 1.5),
        "max_concentration": 10.0,
        "vitals_constraints": {}
    },
    "Ativan": {
        "normal_dose_range": (1, 4),
        "max_concentration": 4.0,
        "vitals_constraints": {}
    },
    "Diltiazem": {
        "normal_dose_range": (0.25, 0.35),
        "max_concentration": 5.0,
        "vitals_constraints": {"FC_min": 50}
    },
    "Adénosine": {
        "normal_dose_range": (6, 12),
        "max_concentration": 3.0,
        "vitals_constraints": {}
    },
    "Phényléphrine": {
        "normal_dose_range": (0.1, 0.25),
        "max_concentration": 10.0,
        "vitals_constraints": {}
    },
    "Chlorure de calcium": {
        "normal_dose_range": (2, 5),
        "max_concentration": 100.0,
        "vitals_constraints": {}
    },
    "Bicarbonate de sodium": {
        "normal_dose_range": (50, 100),
        "max_concentration": 1000.0,
        "vitals_constraints": {}
    },
    "Sulfate de magnésium": {
        "normal_dose_range": (1, 2),
        "max_concentration": 500.0,
        "vitals_constraints": {}
    },
    "Naloxone": {
        "normal_dose_range": (0.4, 2.0),
        "max_concentration": 1.0,
        "vitals_constraints": {}
    },
    "Soluté physiologique": {
        "normal_dose_range": (0, 500),
        "max_concentration": 1.0,
        "vitals_constraints": {}
    }
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
        "explanation": ""
    }
    
    # Vérifier si c'est un médicament connu
    if medication not in MEDICATION_RULES:
        return result
    
    rules = MEDICATION_RULES[medication]
    
    # Les perfusions n'ont pas d'erreurs selon les consignes
    if admin_route.lower() == "perfusion":
        return result
    
    # Vérifier les contraintes vitales
    vitals_constraints = rules.get("vitals_constraints", {})
    if "FC_min" in vitals_constraints and FC < vitals_constraints["FC_min"]:
        result["has_error"] = True
        result["error_type"] = "contrainte_vitale"
        result["severity"] = "danger"
        result["explanation"] = f"{medication}: FC trop basse ({FC} bpm) - risque"
        return result
    
    if "FC_max" in vitals_constraints and FC > vitals_constraints["FC_max"]:
        result["has_error"] = True
        result["error_type"] = "contrainte_vitale"
        result["severity"] = "attention"
        result["explanation"] = f"{medication}: FC très élevée ({FC} bpm)"
        return result
    
    if "TA_sys_min" in vitals_constraints and TA_sys < vitals_constraints["TA_sys_min"]:
        result["has_error"] = True
        result["error_type"] = "contrainte_vitale"
        result["severity"] = "danger"
        result["explanation"] = f"{medication}: TAS trop basse ({TA_sys} mmHg)"
        return result
    
    # Vérifier la dose
    min_dose, max_dose = rules.get("normal_dose_range", (0, 1000))
    if dose < min_dose or dose > max_dose:
        result["has_error"] = True
        result["error_type"] = "dose_inappropriée"
        result["severity"] = "danger" if dose > max_dose * 2 else "attention"
        result["explanation"] = f"{medication}: Dose {dose} ml hors normes ({min_dose}-{max_dose} ml)"
        return result
    
    # Vérifier la concentration
    max_conc = rules.get("max_concentration", 1000)
    if concentration > max_conc:
        result["has_error"] = True
        result["error_type"] = "concentration_inappropriée"
        result["severity"] = "danger"
        result["explanation"] = f"{medication}: Concentration {concentration} mg/mL dépasse le max ({max_conc})"
        return result
    
    return result


def analyze_patient_record(df):
    """
    Analyse un enregistrement patient complet (toutes les lignes avec même ID)
    Retourne liste des erreurs détectées
    """
    errors = []
    
    for idx, row in df.iterrows():
        error = detect_medication_error(row)
        if error["has_error"]:
            error["row_number"] = idx + 2  # +2 car en-tête + índex 0
            error["medication"] = row["Médicament"]
            error["time"] = row.get("Heure", "?")
            errors.append(error)
    
    return errors

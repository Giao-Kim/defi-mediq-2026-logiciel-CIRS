# defi-mediq-2026-logiciel
CIRS - CHARIOT INTELLIGENT DE RÉANIMATION SÉCURISÉE

Le problème:

Nous avons un cas de choc chez un patient et des médicaments doivent être administrés rapidement. Cependant, administrer un médicament peut mener a des erreurs humaines telles que l'administration d'un mauvais médicament, ou l'administration d'un mauvais dosage. 

Solution logiciel:

Implémenter un algorithme capables d'identifier des erreurs médicamenteuses. Un fichier CSV contenant l'identifiant du patient, ses signes vitaux, le médicament administré, la dose admninistrée, la méthode d'admninistration et le volume de perfusion. 

Pour le contexte de ce projet, seul les données du tableau nous sommes données, une seule erreure est présente par patient,  les erreurs sont seulement des médications qu’il ne faudrait pas donner ou dans un dosage différent dans la situation clinique, et la colonne volume de perfusion est négligée. 

Nous avons implémenter notre logiciel avec le language Python supporté par Streamlit comme interface utilisateur:

1) fichier main.py
    - Ouvre le fichier CSV et récupère ces données (une condition est implémenté si l'ouverture du fichier échoue)
    - Appel de la fonction analyze_patient_record() pour chaque patient unique 
    - Print d'erreurs pour chaque patient avec la raison de l'erreur

2) fichier medication_rules.py 


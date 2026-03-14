# defi-mediq-2026-logiciel
CIRS - CHARIOT INTELLIGENT DE RÉANIMATION SÉCURISÉE

Le problème:

Nous avons un cas de choc chez un patient et des médicaments doivent être administrés rapidement. Cependant, administrer un médicament peut mener a des erreurs humaines telles que l'administration d'un mauvais médicament, ou l'administration d'un mauvais dosage. 

Solution logiciel:

Implémenter un algorithme capables d'identifier des erreurs médicamenteuses. Un fichier CSV contenant l'identifiant du patient, ses signes vitaux, le médicament administré, la dose admninistrée, la méthode d'admninistration et le volume de perfusion. 

Pour le contexte de ce projet, seul les données du tableau nous sommes données, une seule erreure est présente par patient,  les erreurs sont seulement des médications qu’il ne faudrait pas donner ou dans un dosage différent dans la situation clinique, et la colonne volume de perfusion est négligée. 

Nous avons décider de suivre ces normes pour le bon dosage de médicament:
Adénosine	3	2	2	4	IV		
Amiodarone	50	6	3	9	IV	Perfusion	
Ativan	2	1	0,25	2	IV	IM	
Atropine	0,1	10	5	30	IV		
Bicarbonate de sodium (mEq/mL)	1	50	50	100	IV		
Chlorure de calcium	100	10	5	20	IV		
Dextrose	500	50	25	100	IV		
Diltiazem	5	4	2	5	IV		
Épinéphrine	0,1	10	10	10	IV	IO	
Fentanyl	0,05	1	0,5	2	IV		
Insuline (U/mL)	100	0,1	0,01	0,1	IV		
Naloxone	0,4	1	1	5	IV	IM	SC
Norépinéphrine	0,016	1	0,5	2	Perfusion		
Phényléphrine	0,1	1	0,5	2	IV	Bolus	
Propofol	10	10,5	7	17,5	IV		
Rocuronium	10	7	4,2	8,4	IV		
Soluté physiologique	1	1000	250	2000	Perfusion		
Sulfate de magnésium	500	4	2	8	IV		

Nous avons implémenter notre logiciel avec le language Python supporté par Streamlit comme interface utilisateur:

1) fichier main.py
    - Ouvre le fichier CSV et récupère ces données (une condition est implémenté si l'ouverture du fichier échoue)
    - Appel de la fonction analyze_patient_record() pour chaque patient unique 
    - Print d'erreurs pour chaque patient avec la raison de l'erreur

2) fichier medication_rules.py 
    - Dicitonnaire:
        Contient les règles de dosage pour 18 médicaments différents. Chaque médicament a:
        normal_dose_range: plage de dose appropriée en mL
        max_concentration: concentration maximale en mg/mL
        vitals_constraints: limites de signes vitaux (FC min/max, TAS min)
        administration_way: voie(s) d'administration correcte(s) (Bolus, IM, Perfusion, etc.)

    - Analyse une ligne de données et détecte 4 types d'erreurs:
        administration_inappropriée: la voie d'administration ne correspond pas aux règles
        contrainte_vitale: les signes vitaux (FC, TAS) sont en dehors des limites permises
        dose_inappropriée: la dose totale (dose × concentration) est hors de la plage normale
    
    - Analyse tous les enregistrements d'un patient et:
        Détecte si un médicament administré en IM change de voie vers autre chose (erreur)
        Applique la fonction detect_medication_error() à chaque ligne
        Retourne une liste de toutes les erreurs trouvées avec numéro de ligne et heure

3) fichier app.py
    - Analyse tous les patients et détecte toutes les erreurs
    - Affiche un tableau avec les erreurs trouvées (Patient, Heure, Médicament, Type, Sévérité)
    - Code couleur: rouge pour "danger", orange pour "attention"
    - Message succès si aucune erreur


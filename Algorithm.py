import string
from nltk.corpus import wordnet as wn
import random
import pandas as pd

specialty_to_subspecialties = {
    "Cardiology": ["Interventional Cardiology", "Electrophysiology", "Heart Failure", "Pediatric Cardiology", "Cardiac Imaging"],
    "Dermatology": ["Pediatric Dermatology", "Cosmetic Dermatology", "Dermatopathology", "Mohs Surgery"],
    "Emergency Medicine": ["Toxicology", "Ultrasound", "Disaster Medicine", "Pediatric Emergency Medicine"],
    "Endocrinology": ["Diabetes", "Thyroid Disorders", "Adrenal Disorders", "Pituitary Disorders"],
    "Family Medicine": ["Preventive Care", "Geriatric Medicine", "Adolescent Medicine", "Women's Health"],
    "Gastroenterology": ["Hepatology", "Inflammatory Bowel Disease", "Pancreatology", "Advanced Endoscopy"],
    "General Surgery": ["Trauma Surgery", "Minimally Invasive Surgery", "Breast Surgery", "Colorectal Surgery"],
    "Geriatrics": ["Memory Disorders", "Palliative Care", "Multimorbidity", "Falls and Balance"],
    "Hematology": ["Leukemia", "Lymphoma", "Coagulation Disorders", "Anemia"],
    "Infectious Diseases": ["HIV/AIDS", "Tropical Diseases", "Antimicrobial Stewardship", "Tuberculosis"],
    "Internal Medicine": ["Hospital Medicine", "Primary Care", "Clinical Pharmacology", "Medical Oncology"],
    "Nephrology": ["Chronic Kidney Disease", "Dialysis", "Transplant Nephrology", "Glomerular Diseases"],
    "Neurology": ["Stroke", "Epilepsy", "Multiple Sclerosis", "Neuromuscular Disorders"],
    "Obstetrics and Gynecology": ["Maternal-Fetal Medicine", "Gynecologic Oncology", "Reproductive Endocrinology", "Urogynecology"],
    "Oncology": ["Breast Cancer", "Lung Cancer", "Palliative Oncology", "Hematologic Malignancies"],
    "Ophthalmology": ["Retina", "Glaucoma", "Cornea", "Pediatric Ophthalmology"],
    "Orthopedics": ["Sports Medicine", "Joint Replacement", "Pediatric Orthopedics", "Spine Surgery"],
    "Otolaryngology": ["Rhinology", "Laryngology", "Otology", "Head and Neck Surgery"],
    "Pediatrics": ["Pediatric Cardiology", "Pediatric Neurology", "Pediatric Endocrinology", "Pediatric Infectious Diseases"],
    "Plastic Surgery": ["Reconstructive Surgery", "Aesthetic Surgery", "Burn Surgery", "Craniofacial Surgery"],
    "Psychiatry": ["Child and Adolescent Psychiatry", "Addiction Psychiatry", "Forensic Psychiatry", "Geriatric Psychiatry"],
    "Pulmonology": ["Sleep Medicine", "Critical Care", "Interstitial Lung Disease", "Pulmonary Hypertension"],
    "Radiology": ["Neuroradiology", "Interventional Radiology", "Musculoskeletal Radiology", "Breast Imaging"],
    "Rheumatology": ["Lupus", "Rheumatoid Arthritis", "Vasculitis", "Spondyloarthritis"],
    "Urology": ["Pediatric Urology", "Urologic Oncology", "Female Urology", "Endourology"]
}

subspecialty_keywords = {
    "Interventional Cardiology": ["stent", "angioplasty", "catheter", "coronary", "artery", "blockage", "ischemia"],
    "Electrophysiology": ["arrhythmia", "palpitations", "pacemaker", "ECG", "irregular heartbeat", "tachycardia"],
    "Heart Failure": ["shortness of breath", "fatigue", "fluid retention", "swollen ankles", "CHF", "weak heart"],
    "Pediatric Cardiology": ["congenital heart", "blue baby", "heart murmur", "child", "pediatric", "cyanosis"],
    "Cardiac Imaging": ["echocardiogram", "MRI heart", "CT angiogram", "cardiac ultrasound"],

    "Pediatric Dermatology": ["eczema", "rashes", "chickenpox", "diaper rash", "child", "skin bumps"],
    "Cosmetic Dermatology": ["botox", "fillers", "laser", "acne scars", "wrinkle treatment"],
    "Dermatopathology": ["skin biopsy", "melanoma", "skin cancer", "basal cell", "histopathology"],
    "Mohs Surgery": ["skin cancer removal", "precise excision", "basal cell", "surgical margins"],

    "Toxicology": ["overdose", "poisoning", "toxins", "drug ingestion", "chemical exposure", "antidote"],
    "Ultrasound": ["FAST scan", "ultrasound trauma", "internal bleeding", "POCUS"],
    "Disaster Medicine": ["earthquake", "mass casualty", "triage", "injury", "disaster response"],
    "Pediatric Emergency Medicine": ["fever in infant", "seizure", "trauma child", "difficulty breathing"],

    "Diabetes": ["high blood sugar", "insulin", "glucose", "polyuria", "polydipsia", "HbA1c"],
    "Thyroid Disorders": ["hypothyroidism", "hyperthyroidism", "goiter", "TSH", "fatigue", "weight change"],
    "Adrenal Disorders": ["Addison’s", "Cushing's", "cortisol", "electrolyte imbalance"],
    "Pituitary Disorders": ["growth hormone", "acromegaly", "prolactin", "pituitary tumor"],

    "Hospital Medicine": ["inpatient", "hospitalized", "rounds", "ward", "discharge", "admission"],
    "Primary Care": ["check-up", "follow-up", "routine care", "health maintenance", "chronic disease"],
    "Clinical Pharmacology": ["drug interaction", "dose adjustment", "side effects", "pharmacokinetics"],
    "Medical Oncology": ["chemotherapy", "cancer treatment", "tumor", "radiation", "metastasis"],

    "Chronic Kidney Disease": ["creatinine", "proteinuria", "dialysis", "kidney function", "nephron loss"],
    "Dialysis": ["hemodialysis", "peritoneal dialysis", "access site", "fluid removal", "ESRD"],
    "Transplant Nephrology": ["kidney transplant", "rejection", "immunosuppression", "donor", "recipient"],
    "Glomerular Diseases": ["proteinuria", "nephrotic syndrome", "glomerulonephritis", "edema", "urinalysis"],

    "Stroke": ["sudden weakness", "slurred speech", "drooping face", "CT head", "clot", "TIA"],
    "Epilepsy": ["seizure", "convulsion", "aura", "EEG", "anti-epileptic"],
    "Multiple Sclerosis": ["vision loss", "tingling", "numbness", "relapsing", "neurological"],
    "Neuromuscular Disorders": ["muscle weakness", "ALS", "myasthenia", "EMG", "fatigue"],

    "Maternal-Fetal Medicine": ["high-risk pregnancy", "gestational diabetes", "ultrasound", "preterm labor"],
    "Gynecologic Oncology": ["ovarian cancer", "uterine cancer", "hysterectomy", "tumor markers"],
    "Reproductive Endocrinology": ["infertility", "IVF", "hormonal imbalance", "menstrual cycle"],
    "Urogynecology": ["incontinence", "pelvic floor", "prolapse", "bladder dysfunction"],

    "Breast Cancer": ["lump", "mammogram", "biopsy", "HER2", "hormone receptor"],
    "Lung Cancer": ["cough", "chest pain", "smoking", "mass", "bronchoscopy"],
    "Palliative Oncology": ["pain relief", "terminal", "end-of-life", "supportive care"],
    "Hematologic Malignancies": ["leukemia", "lymphoma", "bone marrow", "chemotherapy"],

    "Retina": ["detached retina", "floaters", "macular degeneration", "vision loss"],
    "Glaucoma": ["eye pressure", "optic nerve", "tunnel vision", "eye drops"],
    "Cornea": ["transplant", "abrasion", "infection", "keratitis", "contact lens"],
    "Pediatric Ophthalmology": ["lazy eye", "strabismus", "blocked tear duct", "child vision"],

    "Sports Medicine": ["injury", "sprain", "ACL tear", "rehab", "athlete"],
    "Joint Replacement": ["hip replacement", "knee surgery", "prosthesis", "arthritis"],
    "Pediatric Orthopedics": ["limp", "fracture", "scoliosis", "growth plate", "clubfoot"],
    "Spine Surgery": ["herniated disc", "spinal fusion", "sciatica", "stenosis"],

    "Rhinology": ["sinus", "nasal congestion", "polyps", "smell loss", "deviated septum"],
    "Laryngology": ["voice change", "hoarseness", "vocal cord", "throat pain"],
    "Otology": ["ear infection", "hearing loss", "tinnitus", "vertigo", "ear discharge"],
    "Head and Neck Surgery": ["thyroid mass", "neck tumor", "lymph node", "ENT cancer"],

    "Pediatric Neurology": ["seizures in child", "development delay", "autism", "headache", "motor skills"],
    "Pediatric Endocrinology": ["growth delay", "early puberty", "diabetes child", "thyroid child"],
    "Pediatric Infectious Diseases": ["fever", "rash", "infections", "vaccines", "antibiotics child"],

    "Reconstructive Surgery": ["scar revision", "trauma repair", "flap surgery", "skin graft"],
    "Aesthetic Surgery": ["cosmetic", "rhinoplasty", "liposuction", "facelift"],
    "Burn Surgery": ["burns", "grafting", "wound care", "fluid resuscitation"],
    "Craniofacial Surgery": ["cleft palate", "skull deformity", "pediatric facial surgery"],

    "Child and Adolescent Psychiatry": ["ADHD", "anxiety", "depression", "autism", "behavioral issues"],
    "Addiction Psychiatry": ["substance abuse", "detox", "rehab", "opioid", "alcohol"],
    "Forensic Psychiatry": ["legal", "competency", "criminal", "mental illness court"],
    "Geriatric Psychiatry": ["memory loss", "agitation", "dementia", "elderly mental health"],

    "Sleep Medicine": ["apnea", "snoring", "CPAP", "insomnia", "daytime fatigue"],
    "Critical Care": ["ICU", "ventilator", "sepsis", "shock", "intubation"],
    "Interstitial Lung Disease": ["fibrosis", "dyspnea", "cough", "CT chest"],
    "Pulmonary Hypertension": ["shortness of breath", "PAH", "RV strain", "heart-lung"],

    "Neuroradiology": ["MRI brain", "stroke imaging", "CT head", "white matter", "contrast"],
    "Interventional Radiology": ["catheter", "embolization", "biopsy", "minimally invasive"],
    "Musculoskeletal Radiology": ["bone scan", "MRI joint", "arthritis imaging", "sports injury"],
    "Breast Imaging": ["mammogram", "ultrasound breast", "BI-RADS", "MRI breast"],

    "Lupus": ["rash", "autoimmune", "ANA positive", "joint pain", "fatigue"],
    "Rheumatoid Arthritis": ["joint stiffness", "morning stiffness", "RF", "anti-CCP"],
    "Vasculitis": ["inflammation vessels", "rash", "fever", "ANCA", "organ damage"],
    "Spondyloarthritis": ["back pain", "HLA-B27", "AS", "enthesitis", "uveitis"],

    "Pediatric Urology": ["bedwetting", "undescended testicle", "UTI child", "phimosis"],
    "Urologic Oncology": ["prostate cancer", "bladder tumor", "kidney mass", "hematuria"],
    "Female Urology": ["incontinence", "bladder control", "pelvic organ prolapse"],
    "Endourology": ["kidney stones", "laser lithotripsy", "ureteroscopy", "stent"],

    "Preventive Care": ["vaccination", "screening", "routine check", "lifestyle counseling", "prevent disease"],
    "Geriatric Medicine": ["elderly", "memory loss", "falls", "polypharmacy", "frailty"],
    "Adolescent Medicine": ["teen health", "puberty", "eating disorders", "mental health", "menstrual issues"],
    "Women's Health": ["pap smear", "birth control", "menopause", "gynecologic exam", "breast exam"],

    "Hepatology": ["liver", "hepatitis", "cirrhosis", "jaundice", "ALT", "AST"],
    "Inflammatory Bowel Disease": ["Crohn’s", "ulcerative colitis", "diarrhea", "bloody stool", "abdominal pain"],
    "Pancreatology": ["pancreatitis", "enzyme", "amylase", "lipase", "abdominal pain"],
    "Advanced Endoscopy": ["ERCP", "EUS", "endoscopic ultrasound", "biliary", "stent placement"],

    "Trauma Surgery": ["gunshot", "stab wound", "internal bleeding", "trauma team", "emergency surgery"],
    "Minimally Invasive Surgery": ["laparoscopic", "keyhole surgery", "small incision", "robotic surgery"],
    "Breast Surgery": ["lumpectomy", "mastectomy", "breast mass", "nipple discharge"],
    "Colorectal Surgery": ["colon cancer", "rectal bleeding", "diverticulitis", "polypectomy"],

    "Memory Disorders": ["Alzheimer’s", "confusion", "forgetfulness", "dementia", "MMSE"],
    "Palliative Care": ["end of life", "comfort care", "pain management", "advanced directive"],
    "Multimorbidity": ["multiple conditions", "polypharmacy", "chronic illness", "complex care"],
    "Falls and Balance": ["fall risk", "unsteady gait", "walker", "hip fracture", "balance assessment"],

    "Leukemia": ["white blood cells", "blast cells", "bone marrow", "fatigue", "infection"],
    "Lymphoma": ["lymph nodes", "B-cell", "swelling", "night sweats", "weight loss"],
    "Coagulation Disorders": ["bleeding", "clotting", "PT", "INR", "hemophilia"],
    "Anemia": ["fatigue", "pale", "hemoglobin", "iron", "weakness"],

    "HIV/AIDS": ["CD4", "viral load", "antiretroviral", "opportunistic infection", "chronic infection"],
    "Tropical Diseases": ["malaria", "dengue", "chikungunya", "travel history", "mosquito"],
    "Antimicrobial Stewardship": ["antibiotic resistance", "de-escalation", "drug choice", "infection control"],
    "Tuberculosis": ["cough", "night sweats", "weight loss", "chest x-ray", "PPD"]

}

stopwords = ['in','what','who','is','a','at','is', 'the', 'an', 'and', 'to', 'from', 'they', 'is', 'are', 'for', 'be', 'with', 'of', 'has', 'have']

def get_keywords(description):
    description = description.translate(str.maketrans('', '', string.punctuation))
    description = description.lower()
    description_split = description.split(' ')
    keywords  = [word for word in description_split if word not in stopwords]
    return keywords



for key in subspecialty_keywords.keys():
    temp_list =[]
    for keyword in subspecialty_keywords[key]:
        split_keyword = keyword.split(' ')
        for k in split_keyword:
            if(not k in stopwords):
                temp_list.append(k)
    subspecialty_keywords[key]=temp_list

def subspecialty_relevance_avg(subspecialty, keyword):
    n_subspecialty_keywords = len(subspecialty_keywords[subspecialty])
    score_sum = 0
    keyword=keyword.replace(" ", "_")
    for ssk in subspecialty_keywords[subspecialty]:
        try:
            sim = wn.synsets(ssk)[0].path_similarity(wn.synsets(keyword)[0])
            if sim is not None:
                score_sum += sim
            else:
                n_subspecialty_keywords -= 1
        except:
            n_subspecialty_keywords-=1
            continue
    if(n_subspecialty_keywords!=0):
        normalized_score = score_sum/n_subspecialty_keywords
        return normalized_score
    else:
        return 0
    
def subspecialty_relevance_max(subspecialty, keyword):
    score = 0
    keyword=keyword.replace(" ", "_")
    for ssk in subspecialty_keywords[subspecialty]:
        try:
            new_score = wn.synsets(ssk)[0].path_similarity(wn.synsets(keyword)[0])
            if(new_score is not None and new_score>score):
                score = new_score
        except:
            continue
    return score

def get_subspecialty_scores(description):
    column1= []
    column2= []
    description_keywords=get_keywords(description)
    for subspecialty in subspecialty_keywords:
        subspecialty_relevance = 0
        for description_keyword in description_keywords:
            subspecialty_relevance +=subspecialty_relevance_max(subspecialty, description_keyword)
        #print(subspecialty+": "+str(subspecialty_relevance))
        column1.append(subspecialty)
        column2.append(subspecialty_relevance)

    return pd.DataFrame({"Subspecialty": column1, "Score":column2}).sort_values("Score", ascending=False).set_index("Subspecialty", drop=True)

def get_sorted_specialists(specialists, description, languages="English"):
    mask = specialists["languages"].apply(
        lambda x: any(lang.strip().lower() in x.lower() for lang in languages.split(" "))
    )
    specialists = specialists.loc[mask].copy()

    specialists = specialists.sample(frac=1).reset_index(drop=True) # shuffle first
    subspecialty_scores = get_subspecialty_scores(description)
    scores = []
    for subspecialties in specialists["sub_specialty"]:
        doctor_score = 0
        for subspecialty in subspecialties.split(", "):
            doctor_score+=subspecialty_scores.loc[subspecialty, "Score"]
        scores.append(doctor_score)

    specialists["score"]=scores
    return specialists.sort_values("score", ascending=False)



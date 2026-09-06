import re
import pandas as pd

# Standardized Work Category Taxonomy
CATEGORY_PATTERNS = {
    'ROAD': [
        r'\broad\b', r'\bbt\s+road\b', r'\bcc\s+road\b', r'\bsadak\b', r'\bmarg\b',
        r'\bconcrete\s+road\b', r'\btar\s+road\b', r'\brasta\b', r'\bnala\b', r'\bculvert\b',
        r'\bdrain\b', r'\bpuliya\b', r'\bside\s+drain\b', r'\binterlocking\b', r'\bpavement\b',
        r'\bfootpath\b', r'\bpassage\b', r'\blane\b', r'\bbridge\b', r'\bcauseway\b'
    ],
    'EDUCATION': [
        r'\bschool\b', r'\bcollege\b', r'\bvidyalaya\b', r'\bmahavidyalaya\b', r'\bclassroom\b',
        r'\bkaksha\b', r'\blibrary\b', r'\bpustakalaya\b', r'\bhostel\b', r'\blab\b',
        r'\blaboratory\b', r'\bcampus\b', r'\bstudent\b', r'\bprimary\s+school\b', r'\bhigh\s+school\b',
        r'\buniversity\b', r'\beducation\b', r'\beducational\b'
    ],
    'HEALTH': [
        r'\bhospital\b', r'\bhealth\b', r'\baspatal\b', r'\bchikitsalaya\b', r'\bclinic\b',
        r'\bdispensary\b', r'\bphc\b', r'\bdhc\b', r'\bward\b', r'\boxygen\b',
        r'\bambulance\b', r'\bmedical\b', r'\bicu\b', r'\bhealth\s+centre\b', r'\bsub-centre\b'
    ],
    'COMMUNITY_BUILDING': [
        r'\bbhavan\b', r'\bbhawan\b', r'\bhall\b', r'\bsamudayik\b', r'\bcommunity\s+hall\b',
        r'\bcommunity\s+centre\b', r'\bauditorium\b', r'\bshed\b', r'\bpassenger\s+shed\b',
        r'\bbus\s+stand\b', r'\bwaiting\s+shed\b', r'\bboundary\s+wall\b', r'\bcrematorium\b',
        r'\bshamshan\b', r'\bkabristan\b', r'\bghat\b', r'\bmultipurpose\s+hall\b', r'\bkalyan\s+mandapam\b',
        r'\bcentre\b', r'\bcenter\b', r'\bbuilding\b'
    ],
    'LIGHTING': [
        r'\blight\b', r'\bsolar\s+light\b', r'\bstreet\s+light\b', r'\bled\b', r'\bhigh\s+mast\b',
        r'\blamp\b', r'\bsolar\s+high\s+mast\b', r'\blighting\b', r'\bsolar\b'
    ],
    'WATER_SUPPLY': [
        r'\bwater\b', r'\bdrinking\s+water\b', r'\btube\s+well\b', r'\btubewell\b', r'\bhand\s+pump\b',
        r'\bhandpump\b', r'\bborewell\b', r'\btank\b', r'\bwater\s+tank\b', r'\bpipeline\b',
        r'\boverhead\s+tank\b', r'\bjal\b', r'\bwell\b', r'\bpump\b', r'\bwater\s+supply\b'
    ],
    'SANITATION': [
        r'\btoilet\b', r'\blavatory\b', r'\blatrine\b', r'\bwashroom\b', r'\bshouchalay\b',
        r'\bsanitation\b', r'\bsewage\b', r'\bcleanliness\b', r'\bsolid\s+waste\b'
    ],
    'ELECTRIFICATION': [
        r'\belectric\b', r'\belectrification\b', r'\btransformer\b', r'\bsub-station\b',
        r'\bpole\b', r'\bwire\b', r'\bpower\b', r'\benergy\b', r'\bbijli\b'
    ],
    'EQUIPMENT': [
        r'\bequipment\b', r'\bcomputer\b', r'\bprinter\b', r'\bbench\b', r'\bfurniture\b',
        r'\bprojector\b', r'\bsmart\s+class\b', r'\bvehicle\b', r'\binstrument\b',
        r'\bapparatus\b', r'\bprocurement\b', r'\bsupply\b'
    ],
    'SPORTS': [
        r'\bsports\b', r'\bstadium\b', r'\bgym\b', r'\bgymnasium\b', r'\bplayground\b',
        r'\bplay\s+ground\b', r'\bcourt\b', r'\bturf\b', r'\bsports\s+complex\b', r'\bpark\b'
    ]
}

COMPILED_PATTERNS = {
    cat: [(p, re.compile(p, re.IGNORECASE)) for p in patterns]
    for cat, patterns in CATEGORY_PATTERNS.items()
}

def classify_work_description(desc):
    """
    Classifies a raw work description string into a standardized work category.
    Returns (category, classification_reason).
    """
    if pd.isna(desc) or not str(desc).strip():
        return 'OTHER', 'Fallback - Description empty or missing'
    
    text = str(desc)
    
    for category, pattern_tuples in COMPILED_PATTERNS.items():
        for pat_str, regex in pattern_tuples:
            if regex.search(text):
                return category, f"Keyword match: '{pat_str}'"
                
    return 'OTHER', 'Fallback - No keyword match found'

def apply_category_classification(df):
    """
    Adds 'standardized_category' and 'category_classification_reason' columns.
    """
    df_out = df.copy()
    work_col = 'Work description' if 'Work description' in df_out.columns else ('Work' if 'Work' in df_out.columns else None)
    
    cats, reasons = [], []
    if work_col:
        for val in df_out[work_col]:
            c, r = classify_work_description(val)
            cats.append(c)
            reasons.append(r)
    else:
        cats = ['OTHER'] * len(df_out)
        reasons = ['Fallback - Work column missing'] * len(df_out)

    df_out['standardized_category'] = cats
    df_out['category_classification_reason'] = reasons
    return df_out

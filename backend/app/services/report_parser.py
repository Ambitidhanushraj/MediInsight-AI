import re

# Each entry: parameter_name -> list of regex patterns (tried in order)
# Patterns capture the first numeric value (int or float) after the label.
_NUM = r"[:\s=]+([0-9]+(?:\.[0-9]+)?)"

_PATTERNS: dict[str, list[str]] = {
    # ── CBC ──────────────────────────────────────────────────────────────────
    "Hemoglobin":        [r"H(?:ae?|e)moglobin(?:\s*\(H[Bb]\))?" + _NUM,
                          r"Hb" + _NUM],
    "Hematocrit":        [r"H(?:ae?|e)matocrit(?:\s*\(Hct\))?" + _NUM,
                          r"Hct" + _NUM,
                          r"PCV" + _NUM],
    "RBC":               [r"Red\s+Blood\s+Cell(?:\s+Count)?" + _NUM,
                          r"R\.?B\.?C\.?" + _NUM,
                          r"Erythrocyte(?:\s+Count)?" + _NUM],
    "WBC":               [r"White\s+Blood\s+Cell(?:\s+Count)?" + _NUM,
                          r"W\.?B\.?C\.?" + _NUM,
                          r"Total\s+Leukocyte(?:\s+Count)?" + _NUM,
                          r"TLC" + _NUM],
    "Platelets":         [r"Platelet(?:\s+Count)?" + _NUM,
                          r"PLT" + _NUM,
                          r"Thrombocyte(?:\s+Count)?" + _NUM],
    "MCV":               [r"Mean\s+Corpuscular\s+Volume" + _NUM,
                          r"MCV" + _NUM],
    "MCH":               [r"Mean\s+Corpuscular\s+H(?:ae?|e)moglobin(?!\s*C)" + _NUM,
                          r"\bMCH\b" + _NUM],
    "MCHC":              [r"Mean\s+Corpuscular.*?Concentration" + _NUM,
                          r"MCHC" + _NUM],
    "RDW":               [r"Red\s+(?:Cell|Blood\s+Cell)\s+Distribution\s+Width" + _NUM,
                          r"RDW" + _NUM],
    "Neutrophils":       [r"Neutrophil(?:s)?(?:\s+\(Abs\))?" + _NUM,
                          r"Poly(?:morphonuclear)?(?:s)?" + _NUM,
                          r"NEUT" + _NUM],
    "Lymphocytes":       [r"Lymphocyte(?:s)?" + _NUM,
                          r"LYMPH" + _NUM],
    "Monocytes":         [r"Monocyte(?:s)?" + _NUM,
                          r"MONO" + _NUM],
    "Eosinophils":       [r"Eosinophil(?:s)?" + _NUM,
                          r"EOS" + _NUM],
    "Basophils":         [r"Basophil(?:s)?" + _NUM,
                          r"BASO" + _NUM],
    # ── Metabolic ────────────────────────────────────────────────────────────
    "Glucose":           [r"(?:Fasting\s+)?(?:Blood\s+)?Glucose" + _NUM,
                          r"FBS" + _NUM,
                          r"Blood\s+Sugar" + _NUM],
    "HbA1c":             [r"H(?:ae?|e)moglobin\s+A1[Cc]" + _NUM,
                          r"HbA1[Cc]" + _NUM,
                          r"Glycated\s+H(?:ae?|e)moglobin" + _NUM],
    "Creatinine":        [r"(?:Serum\s+)?Creatinine" + _NUM,
                          r"Creat\.?" + _NUM],
    "BUN":               [r"Blood\s+Urea\s+Nitrogen" + _NUM,
                          r"\bBUN\b" + _NUM,
                          r"(?:Serum\s+)?Urea" + _NUM],
    "Sodium":            [r"(?:Serum\s+)?Sodium" + _NUM,
                          r"\bNa\b" + _NUM],
    "Potassium":         [r"(?:Serum\s+)?Potassium" + _NUM,
                          r"\bK\+?\b" + _NUM],
    "Calcium":           [r"(?:Serum\s+)?Calcium" + _NUM,
                          r"\bCa\b" + _NUM],
    "Uric Acid":         [r"Uric\s+Acid" + _NUM],
    # ── Lipid panel ──────────────────────────────────────────────────────────
    "Total Cholesterol": [r"Total\s+Cholesterol" + _NUM,
                          r"Cholesterol(?!.*HDL|.*LDL)" + _NUM],
    "LDL":               [r"LDL(?:[\s\-]Cholesterol)?" + _NUM,
                          r"Low[\s\-]Density\s+Lipoprotein" + _NUM],
    "HDL":               [r"HDL(?:[\s\-]Cholesterol)?" + _NUM,
                          r"High[\s\-]Density\s+Lipoprotein" + _NUM],
    "Triglycerides":     [r"Triglyceride(?:s)?" + _NUM,
                          r"TG" + _NUM],
    # ── Liver ────────────────────────────────────────────────────────────────
    "ALT":               [r"(?:Serum\s+)?ALT" + _NUM,
                          r"Alanine\s+(?:Amino)?transferase" + _NUM,
                          r"SGPT" + _NUM],
    "AST":               [r"(?:Serum\s+)?AST" + _NUM,
                          r"Aspartate\s+(?:Amino)?transferase" + _NUM,
                          r"SGOT" + _NUM],
    "ALP":               [r"Alkaline\s+Phosphatase" + _NUM,
                          r"\bALP\b" + _NUM],
    "Bilirubin":         [r"Total\s+Bilirubin" + _NUM,
                          r"Bilirubin\s+(?:Total|\(T\))" + _NUM],
    "Albumin":           [r"(?:Serum\s+)?Albumin" + _NUM],
    # ── Thyroid ──────────────────────────────────────────────────────────────
    "TSH":               [r"(?:Serum\s+)?TSH" + _NUM,
                          r"Thyroid\s+Stimulating\s+Hormone" + _NUM],
    "T3":                [r"(?:Total\s+|Free\s+)?T3" + _NUM,
                          r"Triiodothyronine" + _NUM],
    "T4":                [r"(?:Total\s+|Free\s+)?T4" + _NUM,
                          r"Thyroxine" + _NUM],
    # ── Iron studies ─────────────────────────────────────────────────────────
    "Iron":              [r"(?:Serum\s+)?Iron" + _NUM],
    "Ferritin":          [r"(?:Serum\s+)?Ferritin" + _NUM],
    "TIBC":              [r"Total\s+Iron[\s\-]Binding\s+Capacity" + _NUM,
                          r"TIBC" + _NUM],
    # ── Vitamins / misc ──────────────────────────────────────────────────────
    "Vitamin D":         [r"Vitamin\s+D(?:\s+Total|\s+25[\s\-]OH)?" + _NUM,
                          r"25[\s\-]OH(?:\s+Vitamin)?\s+D" + _NUM],
    "Vitamin B12":       [r"Vitamin\s+B[\s\-]?12" + _NUM,
                          r"Cobalamin" + _NUM],
}


def extract_health_parameters(text: str) -> dict[str, float]:
    """Extract health parameters from report text using multi-pattern regex matching."""
    results: dict[str, float] = {}
    for parameter, patterns in _PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                try:
                    results[parameter] = float(match.group(1))
                except (ValueError, IndexError):
                    pass
                break  # first matching pattern wins
    return results
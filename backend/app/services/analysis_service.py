# Expanded reference ranges covering CBC, metabolic, lipid, thyroid panels
# Unisex adult defaults — overridden per sex/age below
_REFERENCE_RANGES: dict[str, tuple[float, float]] = {
    # CBC
    "Hemoglobin":       (13.5, 17.5),
    "Hematocrit":       (38.3, 48.6),
    "RBC":              (4.5,  6.0),
    "WBC":              (4.5,  11.0),
    "Platelets":        (150.0, 400.0),
    "MCV":              (80.0, 100.0),
    "MCH":              (27.0, 33.0),
    "MCHC":             (31.5, 35.5),
    "RDW":              (11.5, 14.5),
    "Neutrophils":      (40.0, 75.0),
    "Lymphocytes":      (20.0, 45.0),
    "Monocytes":        (2.0,  10.0),
    "Eosinophils":      (1.0,  6.0),
    "Basophils":        (0.0,  1.0),
    # Metabolic
    "Glucose":          (70.0, 100.0),
    "HbA1c":            (4.0,  5.6),
    "Creatinine":       (0.7,  1.3),
    "BUN":              (7.0,  20.0),
    "Sodium":           (136.0, 145.0),
    "Potassium":        (3.5,  5.1),
    "Calcium":          (8.5,  10.2),
    "Uric Acid":        (3.5,  7.2),
    # Lipid panel
    "Total Cholesterol":(0.0,  200.0),
    "LDL":              (0.0,  100.0),
    "HDL":              (40.0, 9999.0),
    "Triglycerides":    (0.0,  150.0),
    # Liver
    "ALT":              (7.0,  56.0),
    "AST":              (10.0, 40.0),
    "ALP":              (44.0, 147.0),
    "Bilirubin":        (0.1,  1.2),
    "Albumin":          (3.4,  5.4),
    # Thyroid
    "TSH":              (0.4,  4.0),
    "T3":               (80.0, 200.0),
    "T4":               (5.0,  12.0),
    # Iron
    "Iron":              (60.0, 170.0),
    "Ferritin":          (12.0, 300.0),
    "TIBC":              (250.0, 370.0),
    # Vitamins
    "Vitamin D":         (30.0, 100.0),
    "Vitamin B12":       (200.0, 900.0),
}

# Sex-specific overrides  {parameter: {"male": range, "female": range}}
_SEX_RANGES: dict[str, dict[str, tuple[float, float]]] = {
    "Hemoglobin":  {"male": (13.5, 17.5), "female": (12.0, 15.5)},
    "Hematocrit":  {"male": (38.3, 48.6), "female": (35.5, 44.9)},
    "RBC":         {"male": (4.5,  6.0),  "female": (4.0,  5.2)},
    "Creatinine":  {"male": (0.7,  1.3),  "female": (0.5,  1.1)},
    "Ferritin":    {"male": (24.0, 336.0),"female": (11.0, 307.0)},
    "HDL":         {"male": (40.0, 9999.0),"female": (50.0, 9999.0)},
    "Uric Acid":   {"male": (3.5,  7.2),  "female": (2.6,  6.0)},
    "ALP":         {"male": (44.0, 147.0),"female": (35.0, 105.0)},
}

# Critical (panic) thresholds — values outside these require URGENT attention
_CRITICAL_THRESHOLDS: dict[str, tuple] = {
    # (critical_low, critical_high) — None means no critical threshold on that side
    "Hemoglobin":   (7.0,   20.0),
    "WBC":          (2.0,   30.0),
    "Platelets":    (50.0,  1000.0),
    "Glucose":      (50.0,  500.0),
    "Sodium":       (120.0, 160.0),
    "Potassium":    (2.5,   6.5),
    "Calcium":      (6.5,   13.0),
    "Creatinine":   (None,  10.0),
    "Bilirubin":    (None,  15.0),
    "ALT":          (None,  1000.0),
    "AST":          (None,  1000.0),
    "HbA1c":        (None,  10.0),
}


def _get_range(name: str, sex: str = None) -> tuple:
    if sex and sex.lower() in ("male", "female"):
        sex_entry = _SEX_RANGES.get(name)
        if sex_entry:
            return sex_entry[sex.lower()]
    return _REFERENCE_RANGES.get(name)


def analyze_parameter(
    name: str,
    value: float,
    sex: str = None,
    age: int = None,
) -> str:
    """Return: Critical Low, Low, Normal, High, Critical High, or Unknown."""
    crit = _CRITICAL_THRESHOLDS.get(name)
    if crit:
        crit_low, crit_high = crit
        if crit_low is not None and value < crit_low:
            return "Critical Low"
        if crit_high is not None and value > crit_high:
            return "Critical High"

    ref = _get_range(name, sex)
    if ref is None:
        return "Unknown"

    low, high = ref
    if value < low:
        return "Low"
    if value > high:
        return "High"
    return "Normal"


def has_critical_values(analysis: dict) -> bool:
    return any(
        v.get("status", "").startswith("Critical")
        for v in analysis.values()
    )
# Condition-specific dietary + lifestyle recommendations
_RULES: list = [
    # CBC / Anaemia
    {"param": "Hemoglobin", "status": ["Critical Low"],
     "tip": "\u26a0\ufe0f CRITICAL: Hemoglobin is dangerously low. Seek immediate medical attention."},
    {"param": "Hemoglobin", "status": ["Low"],
     "tip": "Eat iron-rich foods: spinach, lentils, red meat, tofu. Pair with vitamin C (orange juice) for better absorption. Avoid tea/coffee with meals."},
    {"param": "RBC", "status": ["Low", "Critical Low"],
     "tip": "Low RBC may indicate anaemia. Increase iron, folate (leafy greens, beans), and vitamin B12 (eggs, dairy, meat). Consult a doctor."},
    {"param": "WBC", "status": ["Critical Low"],
     "tip": "\u26a0\ufe0f CRITICAL: Dangerously low white blood cells. High infection risk. Seek immediate medical care."},
    {"param": "WBC", "status": ["High", "Critical High"],
     "tip": "Elevated WBC may indicate infection, inflammation, or rarely leukaemia. Consult a doctor promptly."},
    {"param": "Platelets", "status": ["Critical Low"],
     "tip": "\u26a0\ufe0f CRITICAL: Platelet count dangerously low. Severe bleeding risk. Seek emergency care."},
    {"param": "Platelets", "status": ["Low"],
     "tip": "Low platelets increase bleeding risk. Avoid NSAIDs. Eat papaya leaf, pomegranate. Seek medical evaluation."},
    {"param": "MCV", "status": ["Low"],
     "tip": "Low MCV (microcytic anaemia) often indicates iron deficiency. Increase iron-rich foods and check ferritin + iron studies."},
    {"param": "MCV", "status": ["High"],
     "tip": "High MCV (macrocytic anaemia) suggests B12 or folate deficiency. Eat eggs, dairy, meat, leafy greens. Consider supplementation."},
    {"param": "MCHC", "status": ["Low"],
     "tip": "Low MCHC indicates hypochromic anaemia (likely iron deficiency). Increase iron intake and recheck in 3 months after treatment."},
    # Metabolic
    {"param": "Glucose", "status": ["Critical High"],
     "tip": "\u26a0\ufe0f CRITICAL: Severely high blood glucose. Seek urgent medical care for possible diabetic emergency."},
    {"param": "Glucose", "status": ["High"],
     "tip": "High glucose: reduce refined sugars, white rice, white bread. Increase fibre (oats, legumes). Exercise 30 min/day. Monitor HbA1c."},
    {"param": "Glucose", "status": ["Critical Low"],
     "tip": "\u26a0\ufe0f CRITICAL: Dangerous hypoglycaemia. Take fast-acting carbs immediately (juice, glucose). Seek urgent care if unconscious."},
    {"param": "HbA1c", "status": ["High", "Critical High"],
     "tip": "HbA1c above 5.6% indicates pre-diabetes or diabetes. Target < 7% with diet + medication. Reduce carbohydrates. Check kidney function."},
    {"param": "Creatinine", "status": ["High", "Critical High"],
     "tip": "Elevated creatinine suggests kidney stress. Stay hydrated. Reduce high-protein diet and NSAIDs. Follow up with a nephrologist."},
    {"param": "Potassium", "status": ["Critical Low"],
     "tip": "\u26a0\ufe0f CRITICAL: Severe hypokalaemia — risk of cardiac arrhythmia. Seek emergency care immediately."},
    {"param": "Potassium", "status": ["Critical High"],
     "tip": "\u26a0\ufe0f CRITICAL: Severe hyperkalaemia — life-threatening heart rhythm risk. Seek emergency care immediately."},
    {"param": "Sodium", "status": ["Low", "Critical Low"],
     "tip": "Low sodium may cause confusion and seizures if severe. Do not over-hydrate. Consult a doctor for cause assessment."},
    # Lipid panel
    {"param": "LDL", "status": ["High"],
     "tip": "High LDL increases heart disease risk. Reduce saturated fat (red meat, butter). Eat oats, almonds, olive oil, fatty fish. Exercise 150 min/week."},
    {"param": "Total Cholesterol", "status": ["High"],
     "tip": "High total cholesterol: limit fried foods and trans fats. Add soluble fibre (oats, beans, apples). Consider statin therapy if cardiovascular risk is elevated."},
    {"param": "Triglycerides", "status": ["High"],
     "tip": "High triglycerides: eliminate sugary drinks and refined carbs. Limit alcohol. Eat omega-3 rich foods (salmon, flaxseed, walnuts)."},
    {"param": "HDL", "status": ["Low"],
     "tip": "Low HDL ('good cholesterol'): exercise regularly, quit smoking, eat healthy fats (avocado, nuts, olive oil)."},
    # Liver
    {"param": "ALT", "status": ["High", "Critical High"],
     "tip": "Elevated ALT indicates liver inflammation. Stop alcohol completely. Avoid paracetamol overuse. Eat cruciferous vegetables (broccoli, cauliflower). Recheck in 4-6 weeks."},
    {"param": "AST", "status": ["High", "Critical High"],
     "tip": "High AST may indicate liver or muscle damage. Avoid alcohol and hepatotoxic medications. Consult a gastroenterologist."},
    {"param": "Bilirubin", "status": ["High", "Critical High"],
     "tip": "High bilirubin can cause jaundice. Avoid alcohol and fasting. Stay hydrated. Urgent evaluation needed for liver or bile duct conditions."},
    # Thyroid
    {"param": "TSH", "status": ["High"],
     "tip": "High TSH indicates hypothyroidism. Eat iodine-rich foods (iodised salt, seafood, dairy). Discuss thyroid hormone replacement with an endocrinologist."},
    {"param": "TSH", "status": ["Low"],
     "tip": "Low TSH indicates hyperthyroidism. Limit caffeine and excess iodine. Consult an endocrinologist for treatment."},
    # Iron
    {"param": "Ferritin", "status": ["Low"],
     "tip": "Low ferritin means depleted iron stores. Increase dietary iron now. Supplement with ferrous sulphate after medical advice. Recheck in 3 months."},
    {"param": "Iron", "status": ["Low"],
     "tip": "Low serum iron: eat red meat, legumes, fortified cereals. Take iron with vitamin C for better absorption."},
    # Vitamins
    {"param": "Vitamin D", "status": ["Low"],
     "tip": "Low vitamin D: get 15-20 min sun exposure daily. Eat fatty fish, egg yolks, fortified milk. Supplement 2000 IU/day (confirm dose with doctor)."},
    {"param": "Vitamin B12", "status": ["Low"],
     "tip": "Low B12 causes fatigue and nerve damage. Eat eggs, dairy, meat, shellfish. Vegetarians/vegans must supplement. Severe deficiency needs B12 injections."},
    # Uric acid
    {"param": "Uric Acid", "status": ["High"],
     "tip": "High uric acid (gout risk): drink 2-3 L water daily. Avoid red meat, shellfish, organ meats, alcohol. Eat cherries and low-fat dairy."},
    # Calcium
    {"param": "Calcium", "status": ["Low"],
     "tip": "Low calcium: eat dairy, broccoli, almonds, fortified plant milk. Ensure adequate vitamin D for absorption."},
    {"param": "Calcium", "status": ["Critical High"],
     "tip": "\u26a0\ufe0f CRITICAL: Severely high calcium can cause kidney failure and cardiac issues. Seek urgent medical evaluation."},
]


def generate_recommendations(analysis: dict) -> list:
    recommendations: list = []
    abnormal_found = False

    for parameter, details in analysis.items():
        status = details.get("status", "Unknown")
        if status not in ("Normal", "Unknown"):
            abnormal_found = True
        for rule in _RULES:
            if rule["param"] == parameter and status in rule["status"]:
                if rule["tip"] not in recommendations:
                    recommendations.append(rule["tip"])

    if not abnormal_found:
        recommendations.append(
            "All extracted parameters are within normal limits. Maintain a balanced diet, stay hydrated, and schedule regular health check-ups."
        )

    return recommendations
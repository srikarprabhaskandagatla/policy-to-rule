SAMPLE_POLICIES = {
    "Screening colonoscopy (frequency)":
        "Screening colonoscopy, CPT code 45378, is covered once every 120 "
        "months for average-risk patients aged 45 or older.",

    "Screening mammography (frequency + eligibility)":
        "Screening mammography, code 77067, is covered once every 12 months "
        "for female patients aged 40 or older.",

    "Annual wellness visit (frequency)":
        "The annual wellness visit, code 99397, is covered once every 12 "
        "months for an established patient.",

    "Bone density screening (frequency)":
        "Bone density measurement, code 77080, is covered once every 24 "
        "months for patients aged 65 or older.",
}


SAMPLE_CLAIMS = [
    {"claim_id": "C001", "patient_id": "P1", "code": "45378", "date": "2023-01-10", "age": 50, "gender": "M"},
    {"claim_id": "C002", "patient_id": "P1", "code": "45378", "date": "2024-02-15", "age": 51, "gender": "M"},
    {"claim_id": "C003", "patient_id": "P2", "code": "45378", "date": "2024-03-01", "age": 42, "gender": "F"},
    {"claim_id": "C004", "patient_id": "P3", "code": "77067", "date": "2024-04-01", "age": 45, "gender": "M"},
    {"claim_id": "C005", "patient_id": "P4", "code": "77067", "date": "2024-05-01", "age": 52, "gender": "F"},
    {"claim_id": "C006", "patient_id": "P4", "code": "77067", "date": "2024-09-01", "age": 52, "gender": "F"},
    {"claim_id": "C007", "patient_id": "P5", "code": "99213", "date": "2024-06-01", "age": 60, "gender": "M"},
]
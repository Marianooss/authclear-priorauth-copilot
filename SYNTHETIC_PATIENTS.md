# 👥 Synthetic FHIR Patients - Test Data

AuthClear uses **5 synthetic FHIR R4 patients** to demonstrate different prior authorization scenarios across various medical specialties.

---

## 📋 Patient Roster

| # | Patient | Age | Gender | Condition | Requested Medication | Scenario |
|---|---------|-----|--------|-----------|---------------------|----------|
| 1 | Maria González | 50 | F | Type 2 Diabetes | Ozempic (semaglutide) | ✅ **Complete** - All criteria met |
| 2 | John Smith | 57 | M | Type 2 Diabetes | Ozempic (semaglutide) | ⚠️ **Gaps** - Missing second oral agent trial |
| 3 | Sarah Johnson | 43 | F | Rheumatoid Arthritis | Humira (adalimumab) | ✅ **Complete** - Biologic prior auth |
| 4 | Robert Chen | 46 | M | Obesity + Prediabetes | Ozempic (weight loss) | ⚠️ **Off-label** - Weight management indication |
| 5 | William Martinez | 66 | M | Atrial Fibrillation | Eliquis (apixaban) | ⚠️ **Switch** - Warfarin not working (labile INR) |

---

## 🔍 Detailed Patient Profiles

### **Patient 1: Maria González** (patient_t2dm_complete.json)
**Primary Diagnosis:** Type 2 Diabetes Mellitus (ICD-10: E11.9)

**Clinical Profile:**
- **Age:** 50 years old (DOB: 1975-03-15)
- **Gender:** Female
- **BMI:** 34.2 kg/m² (obese)
- **HbA1c:** 8.9% (poor control, target <7%)
- **Current Medications:**
  - Metformin 1000mg twice daily (>6 months)
  - Glipizide 10mg daily (second-line agent, >3 months)
- **Allergies:** Penicillin

**Prior Auth Scenario:** Requesting Ozempic (J0173)
- ✅ HbA1c > 7.5% (meets criteria)
- ✅ BMI > 30 (meets criteria)
- ✅ Metformin trial > 3 months (meets criteria)
- ✅ Second oral agent (Glipizide) > 3 months (meets criteria)
- **Expected Result:** High confidence approval (90%+)

---

### **Patient 2: John Smith** (patient_t2dm_gaps.json)
**Primary Diagnosis:** Type 2 Diabetes Mellitus (ICD-10: E11.9)

**Clinical Profile:**
- **Age:** 57 years old (DOB: 1968-07-22)
- **Gender:** Male
- **BMI:** 29.8 kg/m² (overweight, not obese)
- **HbA1c:** 9.2% (very poor control)
- **Current Medications:**
  - Metformin 500mg twice daily (only medication)
- **Allergies:** None documented

**Prior Auth Scenario:** Requesting Ozempic (J0173)
- ✅ HbA1c > 7.5% (meets criteria)
- ⚠️ BMI < 30 (borderline, some payers require >30)
- ✅ Metformin trial documented
- ❌ Second oral agent missing (does not meet criteria)
- **Expected Result:** Medium confidence (70%), missing second-line trial

---

### **Patient 3: Sarah Johnson** (patient_rheumatoid_humira.json)
**Primary Diagnosis:** Rheumatoid Arthritis (ICD-10: M05.9)

**Clinical Profile:**
- **Age:** 43 years old (DOB: 1982-11-08)
- **Gender:** Female
- **Disease Activity:** Active, elevated inflammatory markers
- **Lab Results:**
  - Rheumatoid Factor: 68 IU/mL (high, normal <14)
  - Anti-CCP: 142 U/mL (high, normal <20)
  - ESR: 42 mm/h (elevated, normal <20)
  - CRP: 2.8 mg/dL (elevated, normal <1.0)
- **Current DMARDs:**
  - Methotrexate 20mg weekly (>6 months)
  - Hydroxychloroquine 200mg twice daily (>3 months)
  - Prednisone 5mg daily (corticosteroid)
- **TB Screening:** Negative (2024-10-15)
- **Allergies:** Sulfa drugs

**Prior Auth Scenario:** Requesting Humira (J1438)
- ✅ Positive RF and Anti-CCP (meets criteria)
- ✅ Elevated inflammatory markers (meets criteria)
- ✅ TB screening negative (meets criteria)
- ✅ Methotrexate trial >3 months (meets criteria)
- ✅ Second DMARD (Hydroxychloroquine) >3 months (meets criteria)
- **Expected Result:** High confidence approval (85-90%)

---

### **Patient 4: Robert Chen** (patient_obesity_ozempic.json)
**Primary Diagnoses:** Obesity (E66.9), Hypertension (I10), Prediabetes (R73.03)

**Clinical Profile:**
- **Age:** 46 years old (DOB: 1978-05-22)
- **Gender:** Male
- **Weight:** 268 lbs
- **Height:** 70 inches
- **BMI:** 38.4 kg/m² (Class 2 obesity)
- **HbA1c:** 6.2% (prediabetic range, normal <5.7%)
- **Blood Pressure:** 142/88 mmHg (elevated)
- **LDL:** 148 mg/dL (elevated, target <100)
- **Current Medications:**
  - Lisinopril 20mg daily (antihypertensive)
- **Allergies:** None

**Prior Auth Scenario:** Requesting Ozempic for weight management
- ✅ BMI > 30 (meets obesity criteria)
- ✅ Comorbidities (hypertension, prediabetes, dyslipidemia)
- ⚠️ Not diabetic yet (HbA1c 6.2%, prediabetic)
- ⚠️ Off-label use for weight loss (FDA approved Wegovy, not Ozempic)
- **Expected Result:** Medium-low confidence (60-70%), off-label indication

---

### **Patient 5: William Martinez** (patient_cardiac_eliquis.json)
**Primary Diagnoses:** Atrial Fibrillation (I48.91), Hypertension (I10), CHF (I50.9)

**Clinical Profile:**
- **Age:** 66 years old (DOB: 1958-09-14)
- **Gender:** Male
- **Cardiac Status:**
  - CHA2DS2-VASc Score: 4 (high stroke risk)
  - HAS-BLED Score: 2 (moderate bleeding risk)
  - LVEF: 48% (mildly reduced, normal 55-70%)
- **Current Anticoagulation:** Warfarin 5mg daily
  - INR: 1.8 (sub-therapeutic, target 2.0-3.0)
  - Note: "Patient frequently below therapeutic range" (labile INR)
- **Other Medications:**
  - Metoprolol 50mg twice daily (rate control)
  - Furosemide 40mg daily (heart failure)
- **Renal Function:**
  - Creatinine: 1.2 mg/dL (normal 0.7-1.3)
  - eGFR: 62 mL/min/1.73m² (Stage 2 CKD - mild reduction)
- **Allergies:** Aspirin (GI bleeding)

**Prior Auth Scenario:** Requesting Eliquis (apixaban) to replace Warfarin
- ✅ Atrial fibrillation diagnosis (meets criteria)
- ✅ High CHA2DS2-VASc score (anticoagulation indicated)
- ✅ Labile INR on warfarin (justification for switch)
- ✅ eGFR >50 (safe for DOACs)
- ⚠️ Already on anticoagulation (switch, not new start)
- **Expected Result:** High confidence approval (85%), justified switch

---

## 📊 Complexity Distribution

| Complexity | Count | Patients |
|------------|-------|----------|
| **Simple (1 diagnosis)** | 2 | Maria González, John Smith |
| **Moderate (2-3 diagnoses)** | 3 | Sarah Johnson, Robert Chen, William Martinez |
| **High lab complexity** | 2 | Sarah Johnson (4 labs), William Martinez (4 labs + scores) |

---

## 🎯 Test Coverage

These 5 patients provide comprehensive test coverage for:

### **Medical Specialties:**
- ✅ Endocrinology (Type 2 Diabetes)
- ✅ Rheumatology (Rheumatoid Arthritis)
- ✅ Obesity Medicine (Weight Management)
- ✅ Cardiology (Atrial Fibrillation)

### **Drug Classes:**
- ✅ GLP-1 Receptor Agonists (Ozempic/Wegovy)
- ✅ TNF-alpha Inhibitors (Humira)
- ✅ Direct Oral Anticoagulants (Eliquis)

### **Prior Auth Scenarios:**
- ✅ All criteria met (high confidence)
- ✅ Missing criteria (gaps identified)
- ✅ Off-label use (indication mismatch)
- ✅ Medication switch (warfarin → apixaban)
- ✅ Biologic therapy (DMARD failures documented)

### **FHIR Resources:**
- ✅ Patient
- ✅ Condition (diagnoses)
- ✅ MedicationRequest (current meds)
- ✅ Observation (labs, vitals, scores)
- ✅ AllergyIntolerance

---

## 🧪 Testing Usage

```bash
# Parse all 5 patients
python test_synthetic_patients.py

# Use in integration test
python test_integration.py

# Test with A2A Agent (once servers running)
curl -X POST http://localhost:8000/tasks/send \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "content": "{\"fhir_bundle\": $(cat shared/fhir/synthetic_patients/patient_t2dm_complete.json), \"requested_item\": \"Ozempic\", \"payer\": \"generic\"}"
    }
  }'
```

---

## ✅ Verification Results

All 5 patients successfully parse with `a2a_agent.tools.fhir_reader.parse_fhir_bundle()`:

```
OK patient_t2dm_complete.json: Maria González - 1 diag, 2 meds, 2 labs
OK patient_t2dm_gaps.json: John Smith - 1 diag, 1 meds, 2 labs
OK patient_rheumatoid_humira.json: Sarah Johnson - 1 diag, 3 meds, 4 labs
OK patient_obesity_ozempic.json: Robert Chen - 3 diag, 1 meds, 5 labs
OK patient_cardiac_eliquis.json: William Martinez - 3 diag, 3 meds, 4 labs
```

---

## 📝 Data Source

All patients are **100% synthetic** - generated manually following FHIR R4 specifications.

**No real PHI used.** Safe for demo, testing, and public repositories.

**Compliance:** Meets HIPAA safe harbor requirements (synthetic data, no real patient information).

---

**Created:** 2026-03-30
**Format:** FHIR R4 Bundle
**Purpose:** AuthClear hackathon demonstration & testing

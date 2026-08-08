import streamlit as st
import datetime
import re

# ============================================================
# PULSEMIND AI — EMERGENCY TRIAGE PROTOTYPE
# ============================================================

st.set_page_config(
    page_title="PulseMind AI — Emergency Triage",
    page_icon="🏥",
    layout="wide",
)

# ============================================================
# 1. CORE TRIAGE FUNCTIONS
# ============================================================

def calculate_risk_score(spo2, heart_rate, systolic_bp, resp_rate, temp):
    """
    Prototype deterministic risk engine based on
    the scoring matrix defined in the PulseMind AI blueprint.
    """

    score = 0
    breakdown = {}

    # -------------------------
    # SpO2
    # -------------------------
    if spo2 <= 91:
        points = 3
    elif spo2 <= 93:
        points = 2
    elif spo2 <= 95:
        points = 1
    else:
        points = 0

    score += points
    breakdown["SpO₂"] = points

    # -------------------------
    # Heart Rate
    # -------------------------
    if heart_rate >= 131 or heart_rate <= 40:
        points = 3
    elif heart_rate >= 111:
        points = 2
    elif heart_rate >= 91:
        points = 1
    else:
        points = 0

    score += points
    breakdown["Heart Rate"] = points

    # -------------------------
    # Systolic BP
    # -------------------------
    if systolic_bp <= 90 or systolic_bp >= 220:
        points = 3
    else:
        points = 0

    score += points
    breakdown["Systolic BP"] = points

    # -------------------------
    # Respiratory Rate
    # -------------------------
    if resp_rate >= 25 or resp_rate <= 8:
        points = 3
    elif resp_rate >= 21:
        points = 2
    else:
        points = 0

    score += points
    breakdown["Respiratory Rate"] = points

    # -------------------------
    # Temperature
    # -------------------------
    if temp >= 39.1 or temp <= 35.0:
        points = 3
    elif temp >= 38.1:
        points = 2
    else:
        points = 0

    score += points
    breakdown["Temperature"] = points

    return score, breakdown


# ============================================================
# 2. SYMPTOM / RED FLAG ENGINE
# ============================================================

def detect_red_flags(symptom_text):

    text = symptom_text.lower()

    red_flags = {
        "chest pain": [
            r"\bchest pain\b",
            r"\bchest feels heavy\b",
            r"\bchest feels tight\b",
            r"\bchest pressure\b",
        ],

        "breathing difficulty": [
            r"\bshortness of breath\b",
            r"\bbreathless\b",
            r"\bstruggling to breathe\b",
            r"\bdifficulty breathing\b",
        ],

        "stroke symptoms": [
            r"\bface droop\b",
            r"\bfacial droop\b",
            r"\bslurred speech\b",
            r"\bsudden weakness\b",
            r"\bnumbness\b",
        ],
    }

    detected = []

    for category, patterns in red_flags.items():

        for pattern in patterns:

            if re.search(pattern, text):
                detected.append(category)
                break

    return detected


# ============================================================
# 3. ACUITY DECISION ENGINE
# ============================================================

def determine_esi(spo2, systolic_bp, risk_score, red_flags):

    # -----------------------------------------
    # LEVEL 1 — Immediate Life-Saving
    # -----------------------------------------
    # Deterministic critical physiological triggers
    if (
        spo2 <= 88
        or systolic_bp <= 90 and risk_score >= 7
    ):
        return {
            "level": 1,
            "acuity": "CRITICAL / IMMEDIATE",
            "status": "critical",
        }

    # -----------------------------------------
    # LEVEL 2 — High Risk / Emergent
    # -----------------------------------------
    if (
        risk_score >= 5
        or "chest pain" in red_flags
        or "breathing difficulty" in red_flags
        or "stroke symptoms" in red_flags
    ):
        return {
            "level": 2,
            "acuity": "HIGH RISK / EMERGENT",
            "status": "high",
        }

    # -----------------------------------------
    # LEVEL 3 — Urgent
    # -----------------------------------------
    if risk_score >= 2:
        return {
            "level": 3,
            "acuity": "URGENT / MODERATE",
            "status": "urgent",
        }

    # -----------------------------------------
    # LEVEL 4/5 would require more clinical
    # information in a full implementation.
    # -----------------------------------------
    return {
        "level": 3,
        "acuity": "URGENT / MODERATE",
        "status": "urgent",
    }


# ============================================================
# 4. ESCALATION ENGINE
# ============================================================

def generate_escalation(esi):

    if esi["level"] == 1:

        return {
            "title": "🚨 CRITICAL ALERT",
            "message": "Immediate clinical escalation required.",
            "actions": [
                "Resuscitation team notification",
                "Charge nurse alert",
                "ER physician alert",
                "Priority resuscitation bay routing",
            ],
        }

    elif esi["level"] == 2:

        return {
            "title": "⚠️ HIGH-RISK ALERT",
            "message": "Priority physician assessment required.",
            "actions": [
                "Charge nurse notification",
                "Physician notification",
                "Priority queue assignment",
                "Continuous vital monitoring",
            ],
        }

    else:

        return {
            "title": "🟢 URGENT PATIENT",
            "message": "Patient requires clinical assessment.",
            "actions": [
                "Standard urgent queue",
                "Continue vital monitoring",
            ],
        }


# ============================================================
# 5. FHIR OBSERVATION GENERATOR
# ============================================================

def create_fhir_payload(
    patient_id,
    esi_level,
    risk_score,
    spo2,
    heart_rate,
    systolic_bp,
    resp_rate,
    temperature,
):

    return {
        "resourceType": "Observation",

        "id": f"pulsemind-{patient_id}",

        "status": "final",

        "effectiveDateTime":
            datetime.datetime.now().isoformat(),

        "subject": {
            "reference": f"Patient/{patient_id}"
        },

        "code": {
            "text": "PulseMind AI Emergency Triage Assessment"
        },

        "valueInteger": esi_level,

        "component": [

            {
                "code": {
                    "text": "Risk Score"
                },
                "valueInteger": risk_score
            },

            {
                "code": {
                    "text": "SpO2"
                },
                "valueQuantity": {
                    "value": spo2,
                    "unit": "%"
                }
            },

            {
                "code": {
                    "text": "Heart Rate"
                },
                "valueQuantity": {
                    "value": heart_rate,
                    "unit": "bpm"
                }
            },

            {
                "code": {
                    "text": "Systolic Blood Pressure"
                },
                "valueQuantity": {
                    "value": systolic_bp,
                    "unit": "mmHg"
                }
            },

            {
                "code": {
                    "text": "Respiratory Rate"
                },
                "valueQuantity": {
                    "value": resp_rate,
                    "unit": "breaths/min"
                }
            },

            {
                "code": {
                    "text": "Temperature"
                },
                "valueQuantity": {
                    "value": temperature,
                    "unit": "°C"
                }
            },

        ],
    }


# ============================================================
# 6. USER INTERFACE
# ============================================================

st.title("🏥 PulseMind AI")
st.subheader("Autonomous Medical Triage & Emergency Escalation Agent")

st.markdown(
    "Prototype dashboard for emergency-department triage simulation."
)

st.markdown("---")

col_intake, col_dashboard = st.columns(
    [1, 1.2],
    gap="large"
)


# ============================================================
# LEFT — PATIENT INTAKE
# ============================================================

with col_intake:

    st.header("📋 Patient Intake")

    patient_id = st.text_input(
        "Patient ID",
        "PAT-1004928"
    )

    patient_age = st.number_input(
        "Patient Age",
        min_value=1,
        max_value=110,
        value=78
    )

    st.subheader("Vital Signs")

    spo2 = st.slider(
        "SpO₂ (%)",
        70,
        100,
        89
    )

    heart_rate = st.slider(
        "Heart Rate (BPM)",
        30,
        180,
        118
    )

    systolic_bp = st.slider(
        "Systolic BP (mmHg)",
        60,
        220,
        88
    )

    resp_rate = st.slider(
        "Respiratory Rate",
        8,
        40,
        26
    )

    temperature = st.slider(
        "Temperature (°C)",
        34.0,
        41.0,
        38.2,
        step=0.1
    )

    st.subheader("🗣️ Symptom Intake")

    symptom_text = st.text_area(
        "Voice-to-Text Complaint",
        "My chest feels heavy and tight, and I am struggling to catch my breath."
    )

    analyze = st.button(
        "🚀 Analyze Patient",
        type="primary",
        use_container_width=True
    )


# ============================================================
# RIGHT — CLINICAL DASHBOARD
# ============================================================

with col_dashboard:

    st.header("🚨 ER Clinical Dashboard")

    if analyze:

        # -----------------------------------------
        # STEP 1 — Deterministic Risk Calculation
        # -----------------------------------------

        risk_score, breakdown = calculate_risk_score(
            spo2,
            heart_rate,
            systolic_bp,
            resp_rate,
            temperature
        )

        # -----------------------------------------
        # STEP 2 — NLP Red Flag Detection
        # -----------------------------------------

        red_flags = detect_red_flags(
            symptom_text
        )

        # -----------------------------------------
        # STEP 3 — ESI Decision
        # -----------------------------------------

        esi = determine_esi(
            spo2,
            systolic_bp,
            risk_score,
            red_flags
        )

        # -----------------------------------------
        # STEP 4 — Escalation
        # -----------------------------------------

        escalation = generate_escalation(esi)

        # -----------------------------------------
        # ALERT
        # -----------------------------------------

        if esi["level"] == 1:

            st.error(
                f"{escalation['title']} — "
                f"ESI LEVEL {esi['level']}"
            )

        elif esi["level"] == 2:

            st.warning(
                f"{escalation['title']} — "
                f"ESI LEVEL {esi['level']}"
            )

        else:

            st.success(
                f"{escalation['title']} — "
                f"ESI LEVEL {esi['level']}"
            )

        st.write(
            f"**{escalation['message']}**"
        )

        # -----------------------------------------
        # METRICS
        # -----------------------------------------

        m1, m2, m3 = st.columns(3)

        m1.metric(
            "Risk Score",
            risk_score
        )

        m2.metric(
            "ESI Level",
            f"ESI {esi['level']}"
        )

        m3.metric(
            "Processing",
            "< 1 sec"
        )

        # -----------------------------------------
        # PATIENT SUMMARY
        # -----------------------------------------

        st.markdown("---")

        st.subheader("👤 Patient Summary")

        st.write(
            f"**Patient:** {patient_id}"
        )

        st.write(
            f"**Age:** {patient_age}"
        )

        st.write(
            f"**Acuity:** {esi['acuity']}"
        )

        # -----------------------------------------
        # RED FLAGS
        # -----------------------------------------

        st.subheader("🚩 Detected Clinical Red Flags")

        if red_flags:

            for flag in red_flags:
                st.error(
                    f"Detected: {flag.title()}"
                )

        else:

            st.success(
                "No predefined red-flag symptoms detected."
            )

        # -----------------------------------------
        # VITAL SCORE BREAKDOWN
        # -----------------------------------------

        with st.expander(
            "📊 View Deterministic Risk Breakdown"
        ):

            for vital, points in breakdown.items():

                st.write(
                    f"**{vital}:** +{points} points"
                )

        # -----------------------------------------
        # ESCALATION ACTIONS
        # -----------------------------------------

        st.subheader("📢 Automated Escalation Actions")

        for action in escalation["actions"]:

            st.write(
                f"• {action}"
            )

        # -----------------------------------------
        # FHIR OUTPUT
        # -----------------------------------------

        st.markdown("---")

        st.subheader(
            "🔗 HL7 FHIR Observation"
        )

        fhir_payload = create_fhir_payload(
            patient_id,
            esi["level"],
            risk_score,
            spo2,
            heart_rate,
            systolic_bp,
            resp_rate,
            temperature
        )

        with st.expander(
            "📄 View FHIR JSON"
        ):

            st.json(
                fhir_payload
            )

    else:

        st.info(
            "👈 Enter patient vitals and symptoms, "
            "then click **Analyze Patient**."
        )

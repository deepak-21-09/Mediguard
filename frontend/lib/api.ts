import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { "Content-Type": "application/json" },
  timeout: 5000,
});

export function setAuthToken(token: string | null) {
  if (token) {
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common["Authorization"];
  }
}

// ── Mock data for demo when backend is offline ────────────────────────────

const MOCK_DASHBOARD = {
  health_score: 82,
  active_medications: 3,
  todays_medications: [
    { name: "Metformin", dosage: "500mg", frequency: "twice daily" },
    { name: "Lisinopril", dosage: "10mg", frequency: "once daily" },
    { name: "Atorvastatin", dosage: "20mg", frequency: "once daily at night" },
  ],
  todays_reminders: { total: 4, completed: 2, missed: 1 },
  recent_symptoms: [
    { name: "Mild headache", severity: "mild", logged_at: new Date().toISOString() },
    { name: "Fatigue", severity: "moderate", logged_at: new Date(Date.now() - 86400000).toISOString() },
  ],
  risk_alerts: { total_interactions: 1, critical_interactions: 0 },
  next_appointment: { doctor: "Dr. Sarah Chen", scheduled_at: new Date(Date.now() + 3 * 86400000).toISOString() },
};

const MOCK_MEDICATIONS = [
  { id: "1", name: "Metformin", generic_name: "Metformin HCl", dosage: "500mg", frequency: "twice daily", status: "active", start_date: "2024-01-15", prescribing_doctor: "Dr. Chen", purpose: "Type 2 Diabetes management", reminder_times: ["08:00", "20:00"], created_at: new Date().toISOString() },
  { id: "2", name: "Lisinopril", generic_name: "Lisinopril", dosage: "10mg", frequency: "once daily", status: "active", start_date: "2023-11-01", prescribing_doctor: "Dr. Johnson", purpose: "Hypertension", reminder_times: ["08:00"], created_at: new Date().toISOString() },
  { id: "3", name: "Atorvastatin", generic_name: "Atorvastatin calcium", dosage: "20mg", frequency: "once daily at night", status: "active", start_date: "2023-11-01", prescribing_doctor: "Dr. Johnson", purpose: "High cholesterol", reminder_times: ["21:00"], created_at: new Date().toISOString() },
  { id: "4", name: "Aspirin", generic_name: "Acetylsalicylic acid", dosage: "81mg", frequency: "once daily", status: "active", start_date: "2023-06-01", prescribing_doctor: "Dr. Johnson", purpose: "Cardiovascular prevention", reminder_times: ["08:00"], created_at: new Date().toISOString() },
];

const MOCK_SYMPTOMS = [
  { id: "1", name: "Mild headache", severity: "mild", severity_score: 3, body_location: "head", notes: "After breakfast", ai_analysis: "Could be related to Metformin (GI side effect cascade) or dehydration. Consider drinking more water.", possible_causes: ["Dehydration", "Metformin side effect"], related_medications: ["Metformin"], logged_at: new Date().toISOString() },
  { id: "2", name: "Fatigue", severity: "moderate", severity_score: 5, body_location: null, notes: "Mid-afternoon tiredness", ai_analysis: "Moderate fatigue is a known side effect of Lisinopril in some patients. Pattern consistent with ACE inhibitor fatigue.", possible_causes: ["Lisinopril side effect", "Low blood sugar"], related_medications: ["Lisinopril", "Metformin"], logged_at: new Date(Date.now() - 86400000).toISOString() },
  { id: "3", name: "Dry cough", severity: "mild", severity_score: 2, body_location: "throat", notes: "Persistent for 5 days", ai_analysis: "Dry persistent cough is a very common side effect of ACE inhibitors like Lisinopril, affecting ~20% of patients. Recommend discussing with your doctor — alternatives like ARBs don't cause this.", possible_causes: ["Lisinopril (ACE inhibitor cough)"], related_medications: ["Lisinopril"], logged_at: new Date(Date.now() - 5 * 86400000).toISOString() },
];

const MOCK_APPOINTMENTS = [
  { id: "1", doctor_name: "Dr. Sarah Chen", specialty: "Endocrinology", location: "City Medical Center", scheduled_at: new Date(Date.now() + 3 * 86400000).toISOString(), status: "upcoming", ai_summary: "Patient is managing Type 2 Diabetes with Metformin 500mg twice daily. Blood glucose trends appear stable. Recent symptoms include mild headache and fatigue which may be medication-related.", questions_for_doctor: ["Should I increase my Metformin dosage?", "My dry cough has persisted for 5 days — could it be Lisinopril?", "Are there any lifestyle changes to improve my HbA1c?", "Should I get a kidney function test given my current medications?"], recent_symptoms: ["Mild headache (mild), Fatigue (moderate), Dry cough (mild) — possibly Lisinopril-related"], recent_medication_changes: ["No changes in last 30 days"], notes: null },
  { id: "2", doctor_name: "Dr. Michael Johnson", specialty: "Cardiology", location: "Heart Care Clinic", scheduled_at: new Date(Date.now() + 14 * 86400000).toISOString(), status: "upcoming", ai_summary: null, questions_for_doctor: [], recent_symptoms: [], recent_medication_changes: [], notes: "Annual checkup" },
];

const MOCK_REMINDERS = [
  { id: "1", title: "Take Metformin 500mg", reminder_type: "medication", scheduled_at: new Date().toISOString(), status: "pending" },
  { id: "2", title: "Take Lisinopril 10mg", reminder_type: "medication", scheduled_at: new Date().toISOString(), status: "completed" },
  { id: "3", title: "Atorvastatin 20mg (evening)", reminder_type: "medication", scheduled_at: new Date(Date.now() + 12 * 3600000).toISOString(), status: "pending" },
  { id: "4", title: "Metformin Refill Due", reminder_type: "refill", scheduled_at: new Date(Date.now() + 7 * 86400000).toISOString(), status: "pending" },
];

const MOCK_PROFILE = {
  id: "p1", user_id: "u1",
  age: 58, gender: "Male", weight_kg: 82, height_cm: 175, blood_group: "A+",
  medical_conditions: ["Type 2 Diabetes", "Hypertension", "High Cholesterol"],
  allergies: ["Penicillin"],
  current_diseases: ["Diabetes Mellitus Type 2", "Essential Hypertension"],
  emergency_contact_name: "Jane Doe", emergency_contact_phone: "+1 555 0100", emergency_contact_relation: "Spouse",
  notes: "Patient is diligent about medication compliance.",
};

const MOCK_EMERGENCY = {
  full_name: "John Doe",
  blood_group: "A+",
  allergies: ["Penicillin"],
  active_medications: [
    { name: "Metformin", dosage: "500mg", frequency: "twice daily" },
    { name: "Lisinopril", dosage: "10mg", frequency: "once daily" },
    { name: "Atorvastatin", dosage: "20mg", frequency: "once daily at night" },
    { name: "Aspirin", dosage: "81mg", frequency: "once daily" },
  ],
  emergency_contact_name: "Jane Doe",
  emergency_contact_phone: "+1 555 0100",
  medical_conditions: ["Type 2 Diabetes", "Hypertension", "High Cholesterol"],
};

// ── Helper: try real API, fall back to mock ───────────────────────────────

async function tryOrMock<T>(apiCall: () => Promise<{ data: T }>, mock: T): Promise<{ data: T }> {
  try {
    return await apiCall();
  } catch {
    return { data: mock };
  }
}

// ── API functions ──────────────────────────────────────────────────────────

export const getDashboard = () => tryOrMock(() => api.get("/dashboard"), MOCK_DASHBOARD);

export const getMedications = () => tryOrMock(() => api.get("/medications"), MOCK_MEDICATIONS);
export const addMedication = (data: object) => api.post("/medications", data);
export const updateMedication = (id: string, data: object) => api.put(`/medications/${id}`, data);
export const deleteMedication = (id: string) => api.delete(`/medications/${id}`);
export const scanPrescription = (file: File) => {
  const form = new FormData();
  form.append("file", file);
  return api.post("/medications/scan-prescription", form, { headers: { "Content-Type": "multipart/form-data" } });
};

export const getSymptoms = (days = 90) => tryOrMock(() => api.get(`/symptoms?days=${days}`), MOCK_SYMPTOMS);
export const logSymptom = (data: object) => api.post("/symptoms", data);

export const sendChat = (message: string, sessionId?: string) =>
  api.post("/chat", { message, session_id: sessionId });
export const getChatSessions = () => api.get("/chat/sessions");
export const getSessionMessages = (sessionId: string) => api.get(`/chat/sessions/${sessionId}/messages`);

export const getAppointments = () => tryOrMock(() => api.get("/appointments"), MOCK_APPOINTMENTS);
export const addAppointment = (data: object) => api.post("/appointments", data);
export const getAppointmentSummary = (id: string) => api.post(`/appointments/${id}/summary`);

export const getProfile = () => tryOrMock(() => api.get("/profile"), MOCK_PROFILE);
export const updateProfile = (data: object) => api.put("/profile", data);
export const getEmergencyCard = () => tryOrMock(() => api.get("/profile/emergency-card"), MOCK_EMERGENCY);

export const downloadHealthReport = () =>
  api.get("/reports/health-report.pdf", { responseType: "blob" });

export const getReminders = () => tryOrMock(() => api.get("/reminders"), MOCK_REMINDERS);
export const createReminder = (data: object) => api.post("/reminders", data);
export const updateReminder = (id: string, data: object) => api.patch(`/reminders/${id}`, data);

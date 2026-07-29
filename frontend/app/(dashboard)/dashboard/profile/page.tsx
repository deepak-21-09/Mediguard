"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getProfile, updateProfile } from "@/lib/api";
import { useState, useEffect } from "react";
import { UserCircle, Save } from "lucide-react";

export default function ProfilePage() {
  const qc = useQueryClient();
  const [saved, setSaved] = useState(false);
  const [form, setForm] = useState({
    age: "",
    gender: "",
    weight_kg: "",
    height_cm: "",
    blood_group: "",
    medical_conditions: "",
    allergies: "",
    emergency_contact_name: "",
    emergency_contact_phone: "",
    emergency_contact_relation: "",
    notes: "",
  });

  const { data: profile } = useQuery({
    queryKey: ["profile"],
    queryFn: () => getProfile().then((r) => r.data),
  });

  useEffect(() => {
    if (profile) {
      setForm({
        age: profile.age?.toString() || "",
        gender: profile.gender || "",
        weight_kg: profile.weight_kg?.toString() || "",
        height_cm: profile.height_cm?.toString() || "",
        blood_group: profile.blood_group || "",
        medical_conditions: profile.medical_conditions?.join(", ") || "",
        allergies: profile.allergies?.join(", ") || "",
        emergency_contact_name: profile.emergency_contact_name || "",
        emergency_contact_phone: profile.emergency_contact_phone || "",
        emergency_contact_relation: profile.emergency_contact_relation || "",
        notes: profile.notes || "",
      });
    }
  }, [profile]);

  const updateMutation = useMutation({
    mutationFn: (data: object) => updateProfile(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    },
  });

  const handleSubmit = () => {
    updateMutation.mutate({
      age: form.age ? parseInt(form.age) : null,
      gender: form.gender || null,
      weight_kg: form.weight_kg ? parseFloat(form.weight_kg) : null,
      height_cm: form.height_cm ? parseFloat(form.height_cm) : null,
      blood_group: form.blood_group || null,
      medical_conditions: form.medical_conditions ? form.medical_conditions.split(",").map((s) => s.trim()) : [],
      allergies: form.allergies ? form.allergies.split(",").map((s) => s.trim()) : [],
      emergency_contact_name: form.emergency_contact_name || null,
      emergency_contact_phone: form.emergency_contact_phone || null,
      emergency_contact_relation: form.emergency_contact_relation || null,
      notes: form.notes || null,
    });
  };

  const fields = [
    { key: "age", label: "Age", placeholder: "e.g. 65", type: "number" },
    { key: "gender", label: "Gender", placeholder: "Male / Female / Other" },
    { key: "weight_kg", label: "Weight (kg)", placeholder: "e.g. 70", type: "number" },
    { key: "height_cm", label: "Height (cm)", placeholder: "e.g. 170", type: "number" },
    { key: "blood_group", label: "Blood Group", placeholder: "e.g. A+" },
    { key: "medical_conditions", label: "Medical Conditions", placeholder: "Comma-separated: Diabetes, Hypertension" },
    { key: "allergies", label: "Allergies", placeholder: "Comma-separated: Penicillin, Pollen" },
    { key: "emergency_contact_name", label: "Emergency Contact Name", placeholder: "Jane Doe" },
    { key: "emergency_contact_phone", label: "Emergency Contact Phone", placeholder: "+1 555 0100" },
    { key: "emergency_contact_relation", label: "Relation", placeholder: "Daughter, Spouse..." },
  ];

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <UserCircle className="w-7 h-7 text-[#2563EB]" />
        <h1 className="text-2xl font-bold text-[#1E3A5F]">Health Profile</h1>
      </div>

      <div className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
        <div className="grid grid-cols-2 gap-4">
          {fields.map(({ key, label, placeholder, type }) => (
            <div key={key}>
              <label className="block text-xs text-gray-500 mb-1">{label}</label>
              <input
                type={type || "text"}
                placeholder={placeholder}
                value={form[key as keyof typeof form]}
                onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
              />
            </div>
          ))}
          <div className="col-span-2">
            <label className="block text-xs text-gray-500 mb-1">Notes</label>
            <textarea
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
              placeholder="Any other important health notes..."
              rows={3}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
            />
          </div>
        </div>

        <div className="flex items-center gap-3 mt-6">
          <button
            onClick={handleSubmit}
            disabled={updateMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-[#2563EB] text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50 transition"
          >
            <Save className="w-4 h-4" />
            {updateMutation.isPending ? "Saving..." : "Save Profile"}
          </button>
          {saved && <span className="text-green-600 text-sm">✓ Saved successfully</span>}
        </div>
      </div>
    </div>
  );
}

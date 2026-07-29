"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getMedications, addMedication, deleteMedication, scanPrescription } from "@/lib/api";
import { Plus, Trash2, Upload, AlertTriangle } from "lucide-react";

interface Medication {
  id: string;
  name: string;
  dosage: string;
  frequency: string;
  status: string;
  start_date: string | null;
  prescribing_doctor: string | null;
  purpose: string | null;
}

export default function MedicationsPage() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [interactions, setInteractions] = useState<any[]>([]);
  const [form, setForm] = useState({
    name: "",
    dosage: "",
    frequency: "",
    purpose: "",
    prescribing_doctor: "",
    start_date: "",
  });

  const { data: meds = [], isLoading } = useQuery({
    queryKey: ["medications"],
    queryFn: () => getMedications().then((r) => r.data),
  });

  const addMutation = useMutation({
    mutationFn: (data: object) => addMedication(data),
    onSuccess: (res) => {
      qc.invalidateQueries({ queryKey: ["medications"] });
      qc.invalidateQueries({ queryKey: ["dashboard"] });
      setShowForm(false);
      setForm({ name: "", dosage: "", frequency: "", purpose: "", prescribing_doctor: "", start_date: "" });
      if (res.data.interactions?.length > 0) {
        setInteractions(res.data.interactions);
      }
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteMedication(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["medications"] });
      qc.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  const handleScan = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const res = await scanPrescription(file);
    const meds = res.data.medications || [];
    if (meds.length > 0) {
      const first = meds[0];
      setForm({
        name: first.name || "",
        dosage: first.dosage || "",
        frequency: first.frequency || "",
        purpose: first.purpose || "",
        prescribing_doctor: res.data.prescribing_doctor || "",
        start_date: "",
      });
      setShowForm(true);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[#1E3A5F]">Medications</h1>
          <p className="text-sm text-gray-500">Your complete medication history</p>
        </div>
        <div className="flex gap-3">
          <label className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-lg text-sm cursor-pointer hover:bg-gray-50 transition">
            <Upload className="w-4 h-4" /> Scan Prescription
            <input type="file" accept="image/*" className="hidden" onChange={handleScan} />
          </label>
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 px-4 py-2 bg-[#2563EB] text-white rounded-lg text-sm hover:bg-blue-700 transition"
          >
            <Plus className="w-4 h-4" /> Add Medication
          </button>
        </div>
      </div>

      {/* Interaction warnings */}
      {interactions.length > 0 && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-xl p-4">
          <div className="flex items-center gap-2 text-red-700 font-semibold mb-2">
            <AlertTriangle className="w-5 h-5" />
            Drug Interaction Detected
          </div>
          {interactions.map((i: any, idx: number) => (
            <div key={idx} className="text-sm text-red-600 mb-1">
              <span className="font-medium capitalize">[{i.severity}]</span> Interaction with{" "}
              {i.medication_b_name}: {i.description}
            </div>
          ))}
          <button
            className="mt-2 text-xs text-red-500 underline"
            onClick={() => setInteractions([])}
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Add form */}
      {showForm && (
        <div className="bg-white rounded-2xl border border-gray-100 p-6 mb-6 shadow-sm">
          <h2 className="font-semibold text-[#1E3A5F] mb-4">New Medication</h2>
          <div className="grid grid-cols-2 gap-4">
            {[
              { key: "name", label: "Medication Name", placeholder: "e.g. Metformin" },
              { key: "dosage", label: "Dosage", placeholder: "e.g. 500mg" },
              { key: "frequency", label: "Frequency", placeholder: "e.g. twice daily" },
              { key: "purpose", label: "Purpose", placeholder: "e.g. Diabetes management" },
              { key: "prescribing_doctor", label: "Doctor", placeholder: "Dr. Smith" },
              { key: "start_date", label: "Start Date", placeholder: "", type: "date" },
            ].map(({ key, label, placeholder, type }) => (
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
          </div>
          <div className="flex gap-3 mt-4">
            <button
              onClick={() => addMutation.mutate(form)}
              disabled={addMutation.isPending}
              className="px-4 py-2 bg-[#2563EB] text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50 transition"
            >
              {addMutation.isPending ? "Checking interactions..." : "Save & Check Interactions"}
            </button>
            <button
              onClick={() => setShowForm(false)}
              className="px-4 py-2 border border-gray-200 rounded-lg text-sm hover:bg-gray-50 transition"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Medications list */}
      {isLoading ? (
        <div className="flex justify-center py-16">
          <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent" />
        </div>
      ) : meds.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          No medications recorded. Add your first medication above.
        </div>
      ) : (
        <div className="space-y-3">
          {meds.map((med: Medication) => (
            <div
              key={med.id}
              className="bg-white border border-gray-100 rounded-xl p-4 flex items-center justify-between shadow-sm"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-[#1E3A5F]">{med.name}</span>
                  <StatusBadge status={med.status} />
                </div>
                <div className="text-sm text-gray-500 mt-0.5">
                  {med.dosage} · {med.frequency}
                  {med.prescribing_doctor && ` · Dr. ${med.prescribing_doctor}`}
                </div>
                {med.purpose && (
                  <div className="text-xs text-gray-400 mt-0.5">{med.purpose}</div>
                )}
              </div>
              <button
                onClick={() => deleteMutation.mutate(med.id)}
                className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    active: "bg-green-100 text-green-700",
    stopped: "bg-gray-100 text-gray-600",
    completed: "bg-blue-100 text-blue-700",
    on_hold: "bg-yellow-100 text-yellow-700",
  };
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full capitalize ${colors[status] ?? "bg-gray-100 text-gray-600"}`}>
      {status}
    </span>
  );
}

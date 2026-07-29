"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getAppointments, addAppointment, getAppointmentSummary } from "@/lib/api";
import { Plus, Sparkles, Calendar } from "lucide-react";
import { format } from "date-fns";

export default function AppointmentsPage() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [selectedSummary, setSelectedSummary] = useState<any>(null);
  const [form, setForm] = useState({
    doctor_name: "",
    specialty: "",
    location: "",
    scheduled_at: "",
    notes: "",
  });

  const { data: appointments = [], isLoading } = useQuery({
    queryKey: ["appointments"],
    queryFn: () => getAppointments().then((r) => r.data),
  });

  const addMutation = useMutation({
    mutationFn: (data: object) => addAppointment(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["appointments"] });
      setShowForm(false);
    },
  });

  const summaryMutation = useMutation({
    mutationFn: (id: string) => getAppointmentSummary(id),
    onSuccess: (res) => setSelectedSummary(res.data),
  });

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[#1E3A5F]">Appointments</h1>
          <p className="text-sm text-gray-500">AI prepares you for every doctor visit</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 px-4 py-2 bg-[#2563EB] text-white rounded-lg text-sm hover:bg-blue-700 transition"
        >
          <Plus className="w-4 h-4" /> Add Appointment
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-2xl border border-gray-100 p-6 mb-6 shadow-sm">
          <h2 className="font-semibold text-[#1E3A5F] mb-4">New Appointment</h2>
          <div className="grid grid-cols-2 gap-4">
            {[
              { key: "doctor_name", label: "Doctor Name", placeholder: "Dr. Smith" },
              { key: "specialty", label: "Specialty", placeholder: "Cardiology" },
              { key: "location", label: "Location", placeholder: "City Hospital" },
              { key: "scheduled_at", label: "Date & Time", type: "datetime-local" },
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
              onClick={() => addMutation.mutate({ ...form, scheduled_at: new Date(form.scheduled_at).toISOString() })}
              disabled={addMutation.isPending}
              className="px-4 py-2 bg-[#2563EB] text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50 transition"
            >
              Save
            </button>
            <button onClick={() => setShowForm(false)} className="px-4 py-2 border border-gray-200 rounded-lg text-sm">
              Cancel
            </button>
          </div>
        </div>
      )}

      {selectedSummary && (
        <div className="bg-blue-50 border border-blue-200 rounded-2xl p-6 mb-6">
          <h3 className="font-semibold text-[#1E3A5F] mb-2 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-blue-500" />
            AI Pre-Appointment Summary
          </h3>
          <p className="text-sm text-gray-700 mb-3">{selectedSummary.ai_summary}</p>
          {selectedSummary.questions_for_doctor?.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-gray-500 mb-1">Questions to ask your doctor:</p>
              <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                {selectedSummary.questions_for_doctor.map((q: string, i: number) => (
                  <li key={i}>{q}</li>
                ))}
              </ul>
            </div>
          )}
          <button onClick={() => setSelectedSummary(null)} className="mt-3 text-xs text-blue-500 underline">
            Close
          </button>
        </div>
      )}

      {isLoading ? (
        <div className="flex justify-center py-16">
          <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent" />
        </div>
      ) : appointments.length === 0 ? (
        <div className="text-center py-16 text-gray-400">No appointments scheduled.</div>
      ) : (
        <div className="space-y-3">
          {appointments.map((a: any) => (
            <div key={a.id} className="bg-white border border-gray-100 rounded-xl p-5 flex items-center justify-between shadow-sm">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center">
                  <Calendar className="w-5 h-5 text-[#2563EB]" />
                </div>
                <div>
                  <div className="font-semibold text-[#1E3A5F]">{a.doctor_name}</div>
                  <div className="text-sm text-gray-500">
                    {a.specialty} · {format(new Date(a.scheduled_at), "MMM d, yyyy · h:mm a")}
                  </div>
                  {a.location && <div className="text-xs text-gray-400">{a.location}</div>}
                </div>
              </div>
              <button
                onClick={() => summaryMutation.mutate(a.id)}
                disabled={summaryMutation.isPending}
                className="flex items-center gap-1 px-3 py-1.5 bg-blue-50 text-blue-600 rounded-lg text-xs hover:bg-blue-100 transition"
              >
                <Sparkles className="w-3 h-3" />
                {summaryMutation.isPending ? "Generating..." : "AI Summary"}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

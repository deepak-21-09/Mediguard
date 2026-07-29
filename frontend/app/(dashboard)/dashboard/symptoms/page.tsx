"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getSymptoms, logSymptom } from "@/lib/api";
import { Plus, Brain } from "lucide-react";
import { format } from "date-fns";

export default function SymptomsPage() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    name: "",
    severity: "mild",
    severity_score: "",
    body_location: "",
    duration_hours: "",
    notes: "",
  });

  const { data: symptoms = [], isLoading } = useQuery({
    queryKey: ["symptoms"],
    queryFn: () => getSymptoms(90).then((r) => r.data),
  });

  const logMutation = useMutation({
    mutationFn: (data: object) => logSymptom(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["symptoms"] });
      qc.invalidateQueries({ queryKey: ["dashboard"] });
      setShowForm(false);
      setForm({ name: "", severity: "mild", severity_score: "", body_location: "", duration_hours: "", notes: "" });
    },
  });

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[#1E3A5F]">Symptom Tracker</h1>
          <p className="text-sm text-gray-500">AI analyzes your symptoms against your medications</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-[#2563EB] text-white rounded-lg text-sm hover:bg-blue-700 transition"
        >
          <Plus className="w-4 h-4" /> Log Symptom
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-2xl border border-gray-100 p-6 mb-6 shadow-sm">
          <h2 className="font-semibold text-[#1E3A5F] mb-4">Log a Symptom</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Symptom Name</label>
              <input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="e.g. Headache, Cough, Dizziness"
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Severity</label>
              <select
                value={form.severity}
                onChange={(e) => setForm({ ...form, severity: e.target.value })}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
              >
                <option value="mild">Mild</option>
                <option value="moderate">Moderate</option>
                <option value="severe">Severe</option>
                <option value="critical">Critical</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Body Location (optional)</label>
              <input
                value={form.body_location}
                onChange={(e) => setForm({ ...form, body_location: e.target.value })}
                placeholder="e.g. chest, head"
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Duration (hours)</label>
              <input
                type="number"
                value={form.duration_hours}
                onChange={(e) => setForm({ ...form, duration_hours: e.target.value })}
                placeholder="e.g. 4"
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
              />
            </div>
            <div className="col-span-2">
              <label className="block text-xs text-gray-500 mb-1">Notes</label>
              <textarea
                value={form.notes}
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
                placeholder="Any additional details..."
                rows={2}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
              />
            </div>
          </div>
          <div className="flex gap-3 mt-4">
            <button
              onClick={() => logMutation.mutate({ ...form, duration_hours: form.duration_hours ? parseInt(form.duration_hours) : undefined })}
              disabled={logMutation.isPending || !form.name}
              className="px-4 py-2 bg-[#2563EB] text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50 transition"
            >
              {logMutation.isPending ? "Analyzing with AI..." : "Log & Analyze"}
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

      {isLoading ? (
        <div className="flex justify-center py-16">
          <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent" />
        </div>
      ) : symptoms.length === 0 ? (
        <div className="text-center py-16 text-gray-400">No symptoms logged yet.</div>
      ) : (
        <div className="space-y-4">
          {symptoms.map((s: any) => (
            <div key={s.id} className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-semibold capitalize text-[#1E3A5F]">{s.name}</span>
                  <SeverityBadge severity={s.severity} />
                </div>
                <span className="text-xs text-gray-400">
                  {format(new Date(s.logged_at), "MMM d, yyyy")}
                </span>
              </div>
              {s.ai_analysis && (
                <div className="flex items-start gap-2 bg-blue-50 rounded-lg p-3 mt-2">
                  <Brain className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-blue-700">{s.ai_analysis}</p>
                </div>
              )}
              {s.related_medications?.length > 0 && (
                <div className="mt-2 text-xs text-gray-500">
                  Possibly related to: {s.related_medications.join(", ")}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function SeverityBadge({ severity }: { severity: string }) {
  const colors: Record<string, string> = {
    mild: "bg-green-100 text-green-700",
    moderate: "bg-yellow-100 text-yellow-700",
    severe: "bg-orange-100 text-orange-700",
    critical: "bg-red-100 text-red-700",
  };
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full capitalize font-medium ${colors[severity] ?? "bg-gray-100"}`}>
      {severity}
    </span>
  );
}

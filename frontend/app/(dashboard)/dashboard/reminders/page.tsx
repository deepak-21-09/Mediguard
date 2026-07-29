"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getReminders, createReminder, updateReminder } from "@/lib/api";
import { useState } from "react";
import { Bell, Plus, CheckCircle, Clock } from "lucide-react";
import { format } from "date-fns";

export default function RemindersPage() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: "", scheduled_at: "", reminder_type: "medication" });

  const { data: reminders = [], isLoading } = useQuery({
    queryKey: ["reminders"],
    queryFn: () => getReminders().then((r) => r.data),
  });

  const createMutation = useMutation({
    mutationFn: (data: object) => createReminder(data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["reminders"] }); setShowForm(false); },
  });

  const completeMutation = useMutation({
    mutationFn: (id: string) => updateReminder(id, { status: "completed" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["reminders"] }),
  });

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[#1E3A5F]">Reminders</h1>
          <p className="text-sm text-gray-500">Never miss a dose or appointment</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 px-4 py-2 bg-[#2563EB] text-white rounded-lg text-sm hover:bg-blue-700 transition"
        >
          <Plus className="w-4 h-4" /> Add Reminder
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-2xl border border-gray-100 p-6 mb-6 shadow-sm">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="block text-xs text-gray-500 mb-1">Title</label>
              <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="e.g. Take Metformin 500mg"
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300" />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Type</label>
              <select value={form.reminder_type} onChange={(e) => setForm({ ...form, reminder_type: e.target.value })}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm">
                <option value="medication">Medication</option>
                <option value="appointment">Appointment</option>
                <option value="refill">Refill</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Date & Time</label>
              <input type="datetime-local" value={form.scheduled_at} onChange={(e) => setForm({ ...form, scheduled_at: e.target.value })}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300" />
            </div>
          </div>
          <div className="flex gap-3 mt-4">
            <button onClick={() => createMutation.mutate({ ...form, scheduled_at: new Date(form.scheduled_at).toISOString() })}
              disabled={createMutation.isPending}
              className="px-4 py-2 bg-[#2563EB] text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50 transition">
              Save
            </button>
            <button onClick={() => setShowForm(false)} className="px-4 py-2 border border-gray-200 rounded-lg text-sm">Cancel</button>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="flex justify-center py-16">
          <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent" />
        </div>
      ) : reminders.length === 0 ? (
        <div className="text-center py-16 text-gray-400">No reminders set.</div>
      ) : (
        <div className="space-y-3">
          {reminders.map((r: any) => (
            <div key={r.id} className={`bg-white border rounded-xl p-4 flex items-center justify-between shadow-sm ${r.status === "completed" ? "opacity-60" : "border-gray-100"}`}>
              <div className="flex items-center gap-3">
                <Bell className={`w-5 h-5 ${r.status === "completed" ? "text-green-500" : "text-[#2563EB]"}`} />
                <div>
                  <div className="font-medium text-sm">{r.title}</div>
                  <div className="text-xs text-gray-400 flex items-center gap-1 mt-0.5">
                    <Clock className="w-3 h-3" />
                    {format(new Date(r.scheduled_at), "MMM d, yyyy · h:mm a")}
                  </div>
                </div>
              </div>
              {r.status !== "completed" && (
                <button onClick={() => completeMutation.mutate(r.id)}
                  className="flex items-center gap-1 px-3 py-1.5 text-xs bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition">
                  <CheckCircle className="w-3 h-3" /> Done
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

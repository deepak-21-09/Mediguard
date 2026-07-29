"use client";

import { useQuery } from "@tanstack/react-query";
import { getDashboard } from "@/lib/api";
import {
  Pill,
  Activity,
  AlertTriangle,
  Calendar,
  Heart,
  CheckCircle,
  XCircle,
} from "lucide-react";

export default function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => getDashboard().then((r) => r.data),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  const score = data?.health_score ?? 0;
  const scoreColor =
    score >= 80 ? "text-green-500" : score >= 60 ? "text-yellow-500" : "text-red-500";

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold text-[#1E3A5F] mb-1">Health Dashboard</h1>
      <p className="text-gray-500 text-sm mb-8">Your health overview for today</p>

      {/* Stats grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard
          icon={Heart}
          label="Health Score"
          value={`${score}/100`}
          valueClass={scoreColor}
          bg="bg-blue-50"
        />
        <StatCard
          icon={Pill}
          label="Active Medications"
          value={data?.active_medications ?? 0}
          bg="bg-teal-50"
        />
        <StatCard
          icon={AlertTriangle}
          label="Risk Alerts"
          value={data?.risk_alerts?.critical_interactions ?? 0}
          valueClass={
            (data?.risk_alerts?.critical_interactions ?? 0) > 0 ? "text-red-500" : "text-green-500"
          }
          bg="bg-red-50"
        />
        <StatCard
          icon={Calendar}
          label="Missed Doses Today"
          value={data?.todays_reminders?.missed ?? 0}
          valueClass={
            (data?.todays_reminders?.missed ?? 0) > 0 ? "text-orange-500" : "text-green-500"
          }
          bg="bg-orange-50"
        />
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Today's medications */}
        <div className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
          <h2 className="font-semibold text-[#1E3A5F] mb-4 flex items-center gap-2">
            <Pill className="w-4 h-4" /> Today&apos;s Medications
          </h2>
          {data?.todays_medications?.length > 0 ? (
            <ul className="space-y-2">
              {data.todays_medications.map((m: any, i: number) => (
                <li key={i} className="flex items-center justify-between text-sm">
                  <span className="font-medium">{m.name}</span>
                  <span className="text-gray-400">
                    {m.dosage} · {m.frequency}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-400 text-sm">No medications recorded yet.</p>
          )}
        </div>

        {/* Recent symptoms */}
        <div className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
          <h2 className="font-semibold text-[#1E3A5F] mb-4 flex items-center gap-2">
            <Activity className="w-4 h-4" /> Recent Symptoms
          </h2>
          {data?.recent_symptoms?.length > 0 ? (
            <ul className="space-y-2">
              {data.recent_symptoms.map((s: any, i: number) => (
                <li key={i} className="flex items-center justify-between text-sm">
                  <span className="font-medium capitalize">{s.name}</span>
                  <SeverityBadge severity={s.severity} />
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-400 text-sm">No symptoms logged recently.</p>
          )}
        </div>

        {/* Next appointment */}
        {data?.next_appointment && (
          <div className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
            <h2 className="font-semibold text-[#1E3A5F] mb-3 flex items-center gap-2">
              <Calendar className="w-4 h-4" /> Next Appointment
            </h2>
            <p className="text-lg font-semibold">{data.next_appointment.doctor}</p>
            <p className="text-gray-500 text-sm mt-1">
              {new Date(data.next_appointment.scheduled_at).toLocaleDateString("en-US", {
                weekday: "long",
                year: "numeric",
                month: "long",
                day: "numeric",
              })}
            </p>
          </div>
        )}

        {/* Reminder status */}
        <div className="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
          <h2 className="font-semibold text-[#1E3A5F] mb-4">Today&apos;s Reminder Status</h2>
          <div className="flex gap-6">
            <div className="flex items-center gap-2 text-green-600">
              <CheckCircle className="w-5 h-5" />
              <span className="font-semibold">{data?.todays_reminders?.completed ?? 0}</span>
              <span className="text-sm text-gray-500">completed</span>
            </div>
            <div className="flex items-center gap-2 text-red-500">
              <XCircle className="w-5 h-5" />
              <span className="font-semibold">{data?.todays_reminders?.missed ?? 0}</span>
              <span className="text-sm text-gray-500">missed</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
  valueClass = "text-[#1E3A5F]",
  bg,
}: {
  icon: any;
  label: string;
  value: string | number;
  valueClass?: string;
  bg: string;
}) {
  return (
    <div className={`${bg} rounded-2xl p-5 border border-gray-100`}>
      <Icon className="w-5 h-5 text-gray-500 mb-2" />
      <div className={`text-2xl font-bold ${valueClass}`}>{value}</div>
      <div className="text-xs text-gray-500 mt-1">{label}</div>
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
    <span
      className={`text-xs px-2 py-0.5 rounded-full font-medium capitalize ${
        colors[severity] ?? "bg-gray-100 text-gray-600"
      }`}
    >
      {severity}
    </span>
  );
}

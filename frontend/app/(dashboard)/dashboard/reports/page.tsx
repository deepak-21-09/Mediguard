"use client";

import { useState } from "react";
import { downloadHealthReport } from "@/lib/api";
import { FileText, Download } from "lucide-react";

export default function ReportsPage() {
  const [loading, setLoading] = useState(false);

  const handleDownload = async () => {
    setLoading(true);
    try {
      const res = await downloadHealthReport();
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "mediguard-health-report.pdf");
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      alert("Failed to generate report. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-[#1E3A5F] mb-2">Health Reports</h1>
      <p className="text-sm text-gray-500 mb-8">
        Generate a comprehensive PDF report of your medication history, symptoms, and health data.
      </p>

      <div className="bg-white border border-gray-100 rounded-2xl p-8 shadow-sm text-center">
        <FileText className="w-14 h-14 text-[#2563EB] mx-auto mb-4" />
        <h2 className="text-lg font-semibold text-[#1E3A5F] mb-2">Complete Health Report</h2>
        <p className="text-sm text-gray-500 mb-6">
          Includes your full medication history, recent symptoms, AI insights, and health timeline.
          Share with your doctor or keep for your records.
        </p>
        <button
          onClick={handleDownload}
          disabled={loading}
          className="flex items-center gap-2 px-6 py-3 bg-[#2563EB] text-white rounded-xl mx-auto hover:bg-blue-700 disabled:opacity-50 transition"
        >
          <Download className="w-4 h-4" />
          {loading ? "Generating PDF..." : "Download PDF Report"}
        </button>
      </div>
    </div>
  );
}

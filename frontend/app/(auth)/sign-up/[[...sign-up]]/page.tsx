"use client";

import { useRouter } from "next/navigation";
import { Shield } from "lucide-react";

export default function SignUpPage() {
  const router = useRouter();
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1E3A5F] to-[#2563EB] flex items-center justify-center">
      <div className="bg-white rounded-2xl p-8 w-full max-w-sm shadow-xl">
        <div className="flex items-center gap-2 mb-6">
          <Shield className="w-6 h-6 text-[#2563EB]" />
          <span className="text-xl font-bold text-[#1E3A5F]">MediGuard</span>
        </div>
        <h2 className="text-2xl font-bold text-[#1E3A5F] mb-1">Create account</h2>
        <p className="text-gray-500 text-sm mb-6">Start your health journey</p>
        <input
          type="text"
          placeholder="Full name"
          className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-blue-300"
        />
        <input
          type="email"
          placeholder="Email"
          className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-blue-300"
        />
        <input
          type="password"
          placeholder="Password"
          className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm mb-4 focus:outline-none focus:ring-2 focus:ring-blue-300"
        />
        <button
          onClick={() => router.push("/dashboard")}
          className="w-full py-2.5 bg-[#2563EB] text-white rounded-lg font-semibold hover:bg-blue-700 transition"
        >
          Get Started (Demo)
        </button>
        <p className="text-center text-xs text-gray-400 mt-4">
          Already have an account?{" "}
          <a href="/sign-in" className="text-blue-500 hover:underline">
            Sign in
          </a>
        </p>
      </div>
    </div>
  );
}

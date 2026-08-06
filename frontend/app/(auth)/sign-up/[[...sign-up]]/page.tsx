"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Shield } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function SignUpPage() {
  const router = useRouter();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSignUp = async () => {
    setError("");
    if (!fullName || !email || !password) {
      setError("All fields are required.");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    setLoading(true);
    try {
      // Register via Supabase auth
      const regRes = await fetch(`${API_BASE}/api/v1/auth/supabase/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, full_name: fullName }),
      });

      if (!regRes.ok) {
        const data = await regRes.json().catch(() => ({}));
        setError(data.detail || "Registration failed. The email may already be in use.");
        return;
      }

      const data = await regRes.json();
      const token: string = data.access_token;

      if (!token) {
        // Supabase may require email confirmation before issuing a session
        setError(
          "Account created — please check your email to confirm your address, then sign in."
        );
        return;
      }

      // Set auth cookie
      document.cookie = [
        `auth_token=${token}`,
        "path=/",
        "SameSite=Strict",
        window.location.protocol === "https:" ? "Secure" : "",
      ]
        .filter(Boolean)
        .join("; ");

      const { setAuthToken } = await import("@/lib/api");
      setAuthToken(token);

      router.push("/dashboard");
    } catch {
      setError("Could not connect to the server. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1E3A5F] to-[#2563EB] flex items-center justify-center">
      <div className="bg-white rounded-2xl p-8 w-full max-w-sm shadow-xl">
        <div className="flex items-center gap-2 mb-6">
          <Shield className="w-6 h-6 text-[#2563EB]" />
          <span className="text-xl font-bold text-[#1E3A5F]">MediGuard</span>
        </div>
        <h2 className="text-2xl font-bold text-[#1E3A5F] mb-1">Create account</h2>
        <p className="text-gray-500 text-sm mb-6">Start your health journey</p>

        {error && (
          <div className="mb-4 px-3 py-2 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
            {error}
          </div>
        )}

        <input
          type="text"
          placeholder="Full name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-blue-300"
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-blue-300"
        />
        <input
          type="password"
          placeholder="Password (min. 8 characters)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSignUp()}
          className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm mb-4 focus:outline-none focus:ring-2 focus:ring-blue-300"
        />
        <button
          onClick={handleSignUp}
          disabled={loading}
          className="w-full py-2.5 bg-[#2563EB] text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition"
        >
          {loading ? "Creating account…" : "Get Started"}
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

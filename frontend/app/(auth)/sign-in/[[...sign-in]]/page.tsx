"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Shield } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function SignInPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get("redirect") || "/dashboard";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSignIn = async () => {
    setError("");
    if (!email || !password) {
      setError("Email and password are required.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/auth/supabase/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        setError(data.detail || "Invalid email or password.");
        return;
      }

      const data = await res.json();
      const token: string = data.access_token;

      // Persist the token in a secure, same-site cookie so middleware can read it.
      // HttpOnly is not set here (client-side cookie) so the API client can also
      // read it from document.cookie.  For production with a real domain, prefer
      // an httpOnly cookie set by a Next.js API route.
      document.cookie = [
        `auth_token=${token}`,
        "path=/",
        "SameSite=Strict",
        window.location.protocol === "https:" ? "Secure" : "",
      ]
        .filter(Boolean)
        .join("; ");

      // Also set token in memory for the API client this session
      const { setAuthToken } = await import("@/lib/api");
      setAuthToken(token);

      router.push(redirectTo);
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
        <h2 className="text-2xl font-bold text-[#1E3A5F] mb-1">Welcome back</h2>
        <p className="text-gray-500 text-sm mb-6">Sign in to your account</p>

        {error && (
          <div className="mb-4 px-3 py-2 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
            {error}
          </div>
        )}

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSignIn()}
          className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-blue-300"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSignIn()}
          className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm mb-4 focus:outline-none focus:ring-2 focus:ring-blue-300"
        />
        <button
          onClick={handleSignIn}
          disabled={loading}
          className="w-full py-2.5 bg-[#2563EB] text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition"
        >
          {loading ? "Signing in…" : "Sign In"}
        </button>
        <p className="text-center text-xs text-gray-400 mt-4">
          No account?{" "}
          <a href="/sign-up" className="text-blue-500 hover:underline">
            Sign up
          </a>
        </p>
      </div>
    </div>
  );
}

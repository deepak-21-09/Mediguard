import Link from "next/link";
import { Shield, Brain, Bell, FileText, AlertTriangle, Heart } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1E3A5F] to-[#2563EB] text-white">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-5 max-w-7xl mx-auto">
        <div className="flex items-center gap-2 text-2xl font-bold">
          <Shield className="w-7 h-7 text-teal-300" />
          MediGuard
        </div>
        <div className="flex gap-4">
          <Link
            href="/sign-in"
            className="px-4 py-2 rounded-lg border border-white/30 hover:bg-white/10 transition"
          >
            Sign In
          </Link>
          <Link
            href="/sign-up"
            className="px-4 py-2 rounded-lg bg-white text-[#1E3A5F] font-semibold hover:bg-blue-50 transition"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="text-center py-24 px-8 max-w-4xl mx-auto">
        <div className="inline-flex items-center gap-2 bg-white/10 rounded-full px-4 py-1 text-sm mb-6">
          <span className="w-2 h-2 rounded-full bg-teal-300 animate-pulse" />
          AI-powered medication safety
        </div>
        <h1 className="text-5xl md:text-6xl font-bold leading-tight mb-6">
          One AI that remembers
          <br />
          <span className="text-teal-300">your entire health journey</span>
        </h1>
        <p className="text-lg text-blue-100 mb-10 max-w-2xl mx-auto">
          MediGuard&apos;s MedAgent never forgets a single medication, symptom, or interaction.
          125,000 Americans die yearly from medication errors — we&apos;re here to change that.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/sign-up"
            className="px-8 py-4 bg-teal-400 text-[#1E3A5F] font-bold rounded-xl text-lg hover:bg-teal-300 transition"
          >
            Start for Free
          </Link>
          <Link
            href="#features"
            className="px-8 py-4 border border-white/30 rounded-xl text-lg hover:bg-white/10 transition"
          >
            See How It Works
          </Link>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="bg-white/5 py-20 px-8">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">
            Everything your health needs in one place
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                icon: Brain,
                title: "Persistent AI Memory",
                desc: "Hindsight Memory stores every med, symptom, and conversation — forever. MedAgent recalls it all instantly.",
              },
              {
                icon: AlertTriangle,
                title: "Drug Interaction Detection",
                desc: "Every time you add a medication, MedAgent checks your full history for dangerous interactions.",
              },
              {
                icon: Heart,
                title: "Symptom Pattern Analysis",
                desc: "Log symptoms and let AI connect the dots — like linking a new cough to a pill started days ago.",
              },
              {
                icon: Bell,
                title: "Smart Reminders",
                desc: "Never miss a dose. Smart reminders adapt to your schedule and detect missed medications.",
              },
              {
                icon: FileText,
                title: "Doctor Visit Ready",
                desc: "AI generates a full appointment summary with your symptom timeline and questions to ask.",
              },
              {
                icon: Shield,
                title: "Emergency Card",
                desc: "One tap shows your allergies, blood group, and current meds to any emergency responder.",
              },
            ].map(({ icon: Icon, title, desc }) => (
              <div key={title} className="bg-white/10 rounded-2xl p-6 hover:bg-white/15 transition">
                <Icon className="w-8 h-8 text-teal-300 mb-3" />
                <h3 className="text-lg font-semibold mb-2">{title}</h3>
                <p className="text-blue-100 text-sm">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="text-center py-8 text-blue-200 text-sm">
        © 2025 MediGuard. Not a substitute for professional medical advice.
      </footer>
    </div>
  );
}

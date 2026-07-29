"use client";

import { useState, useRef, useEffect } from "react";
import { sendChat } from "@/lib/api";
import { Send, Bot, User, Shield } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi, I'm MedAgent — your personal AI health assistant. I have access to your complete medication history, symptoms, and health profile. Ask me anything: about your medications, symptoms, interactions, or to prepare for your next doctor visit.",
    },
  ]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const res = await sendChat(userMsg, sessionId);
      setSessionId(res.data.session_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.data.reply },
      ]);
    } catch {
      // Demo fallback when backend is offline
      const demoReplies: Record<string, string> = {
        "cough": "Based on your medication history, your dry persistent cough is most likely caused by Lisinopril — this is a very common side effect of ACE inhibitors, affecting about 20% of patients. I'd strongly recommend discussing switching to an ARB (like Losartan) with Dr. Johnson at your upcoming cardiology appointment.",
        "interaction": "I've reviewed your 4 active medications. I found one notable interaction: Metformin + Atorvastatin can occasionally cause increased muscle weakness risk. It's low severity, but worth monitoring. No critical interactions detected.",
        "doctor": "Here's your pre-appointment summary for Dr. Chen (3 days away): ① Metformin compliance: 100% ② New symptoms: Headache (mild), Fatigue (moderate), Dry cough (5 days — likely Lisinopril) ③ Key questions: Should we adjust Metformin dose? Is the cough from Lisinopril? Any needed lab tests?",
        "side effect": "Looking at your current medications, common side effects to watch for: Metformin — GI upset, lactic acidosis (rare). Lisinopril — dry cough (you've reported this!), dizziness. Atorvastatin — muscle aches. Aspirin — stomach irritation. Your reported fatigue and cough align with known Lisinopril effects.",
      };
      const key = Object.keys(demoReplies).find(k => userMsg.toLowerCase().includes(k));
      const reply = key ? demoReplies[key] : "I'm MedAgent. I can see you have 4 active medications: Metformin, Lisinopril, Atorvastatin, and Aspirin. Your recent symptoms include a dry cough and fatigue. Connect the backend (uvicorn main:app) with your OpenAI API key for full AI responses. Try asking about your cough, drug interactions, or doctor visit prep!";
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } finally {
      setLoading(false);
    }
  };

  const suggestions = [
    "Why might I be coughing?",
    "Check my drug interactions",
    "Prepare me for my next doctor visit",
    "What are the side effects of my medications?",
  ];

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 px-8 py-4 flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-[#1E3A5F] flex items-center justify-center">
          <Shield className="w-5 h-5 text-teal-300" />
        </div>
        <div>
          <div className="font-semibold text-[#1E3A5F]">MedAgent</div>
          <div className="text-xs text-gray-400">Powered by Hindsight Memory · Remembers everything</div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-8 py-6 space-y-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                msg.role === "assistant" ? "bg-[#1E3A5F]" : "bg-[#2563EB]"
              }`}
            >
              {msg.role === "assistant" ? (
                <Bot className="w-4 h-4 text-white" />
              ) : (
                <User className="w-4 h-4 text-white" />
              )}
            </div>
            <div
              className={`max-w-2xl rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                msg.role === "assistant"
                  ? "bg-white border border-gray-100 text-gray-800 shadow-sm"
                  : "bg-[#2563EB] text-white"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-[#1E3A5F] flex items-center justify-center">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="bg-white border border-gray-100 rounded-2xl px-4 py-3 shadow-sm">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce [animation-delay:0ms]" />
                <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce [animation-delay:150ms]" />
                <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce [animation-delay:300ms]" />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Suggestions */}
      {messages.length <= 1 && (
        <div className="px-8 pb-2 flex flex-wrap gap-2">
          {suggestions.map((s) => (
            <button
              key={s}
              onClick={() => setInput(s)}
              className="text-xs px-3 py-1.5 bg-white border border-gray-200 rounded-full text-gray-600 hover:border-blue-300 hover:text-blue-600 transition"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="bg-white border-t border-gray-100 px-8 py-4">
        <div className="flex gap-3 max-w-4xl mx-auto">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="Ask MedAgent about your health..."
            className="flex-1 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
          />
          <button
            onClick={send}
            disabled={!input.trim() || loading}
            className="px-4 py-3 bg-[#2563EB] text-white rounded-xl hover:bg-blue-700 disabled:opacity-40 transition"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

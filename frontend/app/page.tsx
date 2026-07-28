"use client";

import { useState } from "react";
import { Send, Bot, User, BookOpen } from "lucide-react";
import ReactMarkdown from "react-markdown";

// 1. Create a custom URL transformer to allow Base64 data URIs
const customUrlTransform = (url: string) => {
  if (url.startsWith("data:image/")) {
    return url; // Allow our Base64 images
  }
  return url; // Allow standard links
};

export default function Home() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<
    { role: "user" | "bot"; text: string; sources?: string[] }[]
  >([]);
  const [loading, setLoading] = useState(false);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    // Add user message to UI
    const newMessages = [...messages, { role: "user", text: query }];
    setMessages(newMessages as any);
    setQuery("");
    setLoading(true);

    try {
      // Connect to your FastAPI Python backend
      const res = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      if (!res.ok) throw new Error("API failed");

      const data = await res.json();
      
      // Add AI response and citations to UI
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: data.answer, sources: data.sources },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "Error: Could not connect to the RAG backend." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-4xl bg-gray-900 border border-gray-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col h-[85vh]">
        
        {/* Header */}
        <div className="bg-gray-800 p-5 border-b border-gray-700 flex items-center gap-3">
          <BookOpen className="text-emerald-500 w-6 h-6" />
          <h1 className="text-xl font-bold tracking-wide">
            NCAI Biology Assistant
          </h1>
        </div>

        {/* Chat History Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-500 space-y-4">
              <Bot className="w-16 h-16 opacity-50" />
              <p className="text-lg">Ask a question about Class 11 Biology.</p>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div
                key={index}
                className={`flex gap-4 ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {msg.role === "bot" && (
                  <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0">
                    <Bot className="w-5 h-5 text-emerald-400" />
                  </div>
                )}
                
                <div
                  className={`max-w-[80%] rounded-2xl p-4 ${
                    msg.role === "user"
                      ? "bg-emerald-600 text-white"
                      : "bg-gray-800 border border-gray-700 text-gray-200"
                  }`}
                >
                  {/* Markdown Renderer for AI output */}
                  {msg.role === "bot" ? (
                    <div className="prose prose-invert max-w-none">
                      {/* 2. Apply the URL transformer and custom image styling */}
                      <ReactMarkdown 
                        urlTransform={customUrlTransform}
                        components={{
                          img: ({node, ...props}) => (
                            <img 
                              {...props} 
                              className="max-w-full h-auto rounded-lg my-2 border border-gray-700 shadow-sm" 
                              alt={props.alt || "Requested figure"}
                            />
                          )
                        }}
                      >
                        {msg.text}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <p>{msg.text}</p>
                  )}

                  {/* Sources Renderer */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-gray-700">
                      <p className="text-xs font-semibold text-emerald-400 mb-2 tracking-wider uppercase">
                        Sources Used:
                      </p>
                      <ul className="space-y-1">
                        {msg.sources.map((src, i) => (
                          <li key={i} className="text-xs text-gray-400 break-words">
                            {src}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {msg.role === "user" && (
                  <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center shrink-0">
                    <User className="w-5 h-5 text-gray-300" />
                  </div>
                )}
              </div>
            ))
          )}
          {loading && (
            <div className="flex gap-4 justify-start">
              <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center">
                <Bot className="w-5 h-5 text-emerald-400 animate-pulse" />
              </div>
              <div className="bg-gray-800 border border-gray-700 rounded-2xl p-4 animate-pulse text-gray-400">
                Searching textbook and generating response...
              </div>
            </div>
          )}
        </div>

        {/* Input Form */}
        <form
          onSubmit={handleAsk}
          className="p-4 bg-gray-900 border-t border-gray-800"
        >
          <div className="relative flex items-center">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask about annual rings, fluid mosaic model..."
              className="w-full bg-gray-800 border border-gray-700 text-gray-100 rounded-xl pl-4 pr-12 py-4 focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading}
              className="absolute right-2 p-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg transition-colors disabled:opacity-50"
            >
              <Send className="w-5 h-5 text-white" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
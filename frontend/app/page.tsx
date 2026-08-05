"use client";

import React, { useState, useRef, useEffect, ReactNode } from "react";
import {
  Send,
  User,
  Zap,
  Sparkles,
  ChevronDown,
  Copy,
  Check,
  Loader,
  Microscope,
  Beaker,
  TrendingUp, 
  Dna,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import type { Components } from "react-markdown";

// ============================================================================
// STYLES & ANIMATIONS
// ============================================================================

const globalStyles = `
  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
  }
  
  @keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
    50% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
  }
  
  @keyframes slide-in-left {
    from { opacity: 0; transform: translateX(-20px); }
    to { opacity: 1; transform: translateX(0); }
  }
  
  @keyframes slide-in-right {
    from { opacity: 0; transform: translateX(20px); }
    to { opacity: 1; transform: translateX(0); }
  }
  
  @keyframes gradient-shift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
  
  @keyframes dna-helix {
    0% { transform: rotateX(0deg) rotateY(0deg); }
    100% { transform: rotateX(360deg) rotateY(180deg); }
  }
  
  @keyframes bounce-subtle {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
  }
  
  .animate-float { animation: float 3s ease-in-out infinite; }
  .animate-pulse-glow { animation: pulse-glow 2s infinite; }
  .animate-slide-in-left { animation: slide-in-left 0.5s ease-out; }
  .animate-slide-in-right { animation: slide-in-right 0.5s ease-out; }
  .animate-dna { animation: dna-helix 4s linear infinite; }
  .animate-bounce-subtle { animation: bounce-subtle 2s ease-in-out infinite; }
  .gradient-animated {
    background: linear-gradient(-45deg, #10b981, #06b6d4, #8b5cf6, #10b981);
    background-size: 400% 400%;
    animation: gradient-shift 15s ease infinite;
  }
  
  .glass-morphism {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
  }
  
  .text-gradient {
    background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
`;

// ============================================================================
// CUSTOM MARKDOWN COMPONENTS
// ============================================================================

const customUrlTransform = (url: string) => {
  if (url.startsWith("data:image/")) return url;
  return url;
};

const MarkdownComponents = {
  h1: ({ children }: { children: ReactNode }) => (
    <h1 className="text-3xl font-bold text-gradient mt-6 mb-4">{children}</h1>
  ),
  h2: ({ children }: { children: ReactNode }) => (
    <h2 className="text-2xl font-bold text-emerald-400 mt-5 mb-3">{children}</h2>
  ),
  h3: ({ children }: { children: ReactNode }) => (
    <h3 className="text-xl font-semibold text-cyan-400 mt-4 mb-2">{children}</h3>
  ),
  p: ({ children }: { children: ReactNode }) => (
    <p className="text-gray-300 mb-3 leading-relaxed">{children}</p>
  ),
  strong: ({ children }: { children: ReactNode }) => (
    <strong className="text-emerald-300 font-bold">{children}</strong>
  ),
  em: ({ children }: { children: ReactNode }) => (
    <em className="text-cyan-300 italic">{children}</em>
  ),
  code: ({ children, inline }: { children: ReactNode; inline?: boolean }) => (
    <code
      className={`${
        inline
          ? "bg-gray-800 text-emerald-300 px-2 py-1 rounded font-mono text-sm"
          : "block bg-gray-800 text-emerald-300 p-3 rounded font-mono text-sm overflow-x-auto mb-3"
      }`}
    >
      {children}
    </code>
  ),
  ul: ({ children }: { children: ReactNode }) => (
    <ul className="list-disc list-inside mb-3 space-y-2 text-gray-300">
      {children}
    </ul>
  ),
  ol: ({ children }: { children: ReactNode }) => (
    <ol className="list-decimal list-inside mb-3 space-y-2 text-gray-300">
      {children}
    </ol>
  ),
  li: ({ children }: { children: ReactNode }) => <li className="ml-2">{children}</li>,
  table: ({ children }: { children: ReactNode }) => (
    <div className="overflow-x-auto mb-4 rounded-lg border border-gray-700">
      <table className="w-full text-sm">{children}</table>
    </div>
  ),
  thead: ({ children }: { children: ReactNode }) => (
    <thead className="bg-gradient-to-r from-emerald-900 to-cyan-900">
      {children}
    </thead>
  ),
  tbody: ({ children }: { children: ReactNode }) => (
    <tbody className="divide-y divide-gray-700">{children}</tbody>
  ),
  tr: ({ children }: { children: ReactNode }) => <tr className="divide-x divide-gray-700">{children}</tr>,
  th: ({ children }: { children: ReactNode }) => (
    <th className="px-4 py-3 text-left font-bold text-emerald-300">
      {children}
    </th>
  ),
  td: ({ children }: { children: ReactNode }) => (
    <td className="px-4 py-3 text-gray-300">{children}</td>
  ),
  img: ({ src, alt }: { src?: string | null; alt?: string | null }) => {
    if (!src) return null;
    return (
      <div className="my-4 overflow-hidden rounded-xl border-2 border-emerald-500/50 shadow-xl mb-4">
        <img
          src={src}
          alt={alt || "Biology figure"}
          className="w-full h-auto hover:scale-105 transition-transform duration-300"
        />
        {alt && (
          <div className="text-xs text-gray-400 p-2 bg-gray-900 text-center italic">
            {alt}
          </div>
        )}
      </div>
    );
  },
  blockquote: ({ children }: { children: ReactNode }) => (
    <blockquote className="border-l-4 border-emerald-500 pl-4 my-3 italic text-gray-400">
      {children}
    </blockquote>
  ),
};

// ============================================================================
// SUGGESTION CARDS COMPONENT
// ============================================================================

interface SuggestionCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  onClick: () => void;
}

const SuggestionCard = ({
  icon,
  title,
  description,
  onClick,
}: SuggestionCardProps) => (
  <button
    onClick={onClick}
    className="group p-4 rounded-xl bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-700 hover:border-emerald-500 transition-all duration-300 text-left hover:shadow-lg hover:shadow-emerald-500/20 transform hover:-translate-y-1"
  >
    <div className="flex items-start gap-3">
      <div className="text-emerald-400 group-hover:text-emerald-300 transition-colors mt-1">
        {icon}
      </div>
      <div className="flex-1">
        <h3 className="font-semibold text-gray-100 group-hover:text-emerald-300 transition-colors">
          {title}
        </h3>
        <p className="text-xs text-gray-500 group-hover:text-gray-400 transition-colors mt-1">
          {description}
        </p>
      </div>
    </div>
  </button>
);

// ============================================================================
// LOADING ANIMATION COMPONENT
// ============================================================================

const LoadingAnimation = () => (
  <div className="flex gap-4 items-center justify-start animate-slide-in-left">
    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center shrink-0 animate-pulse-glow">
      <Microscope className="w-5 h-5 text-white animate-bounce" />
    </div>
    <div className="flex-1">
      <div className="bg-gradient-to-r from-gray-800 to-gray-700 rounded-xl p-4 space-y-2 glass-morphism">
        <div className="flex gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-bounce" />
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-bounce delay-100" />
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-bounce delay-200" />
        </div>
        <p className="text-sm text-gray-300">Searching through your biology textbook...</p>
      </div>
    </div>
  </div>
);

// ============================================================================
// SOURCE CARD COMPONENT
// ============================================================================

const SourceCard = ({ source, index }: { source: string; index: number }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(source);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="group flex items-start gap-3 p-3 rounded-lg hover:bg-gray-700/50 transition-colors">
      <div className="w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0 text-emerald-400 font-mono text-xs font-bold">
        {index + 1}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-xs text-gray-400 break-words font-mono leading-relaxed">
          {source}
        </p>
      </div>
      <button
        onClick={handleCopy}
        className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-gray-600 rounded"
      >
        {copied ? (
          <Check className="w-4 h-4 text-emerald-400" />
        ) : (
          <Copy className="w-4 h-4 text-gray-400" />
        )}
      </button>
    </div>
  );
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function BiologyRAG() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<
    {
      role: "user" | "bot";
      text: string;
      sources?: string[];
      timestamp?: Date;
    }[]
  >([]);
  const [loading, setLoading] = useState(false);
  const [expandedSources, setExpandedSources] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMessage = query;
    setQuery("");
    setMessages((prev) => [
      ...prev,
      { role: "user", text: userMessage, timestamp: new Date() },
    ]);
    setLoading(true);
    setExpandedSources(null);

    try {
      const res = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userMessage }),
      });

      if (!res.ok) throw new Error("API failed");

      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: data.answer,
          sources: data.sources,
          timestamp: new Date(),
        },
      ]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: "❌ **Error**: Could not connect to the RAG backend. Please check if your FastAPI server is running on `http://localhost:8000`.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestion = (suggestion: string) => {
    setQuery(suggestion);
  };

  return (
    <>
      <style>{globalStyles}</style>

      <div className="min-h-screen bg-gradient-to-br from-gray-950 via-blue-950 to-gray-950 text-gray-100 flex flex-col items-center justify-center p-4">
        {/* Animated Background Elements */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-10 w-72 h-72 bg-emerald-500/10 rounded-full blur-3xl animate-float" />
          <div className="absolute bottom-32 right-10 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-float delay-700" />
          <div className="absolute top-1/2 left-1/2 w-80 h-80 bg-purple-500/5 rounded-full blur-3xl animate-float delay-1000" />
        </div>

        {/* Main Container */}
        <div className="w-full max-w-6xl relative z-10">
          {/* Header */}
          <div className="mb-6">
            <div className="glass-morphism rounded-2xl p-8 text-center border-2 border-emerald-500/30">
              <div className="flex items-center justify-center gap-3 mb-4">
                <div className="text-emerald-400 animate-pulse-glow">
                  <Dna className="w-8 h-8 animate-dna" />
                </div>
                <h1 className="text-4xl font-bold text-gradient">
                  Biology Scholar
                </h1>
                <div className="text-cyan-400 animate-pulse-glow">
                  <Microscope className="w-8 h-8 animate-dna" />
                </div>
              </div>
              <p className="text-gray-300 flex items-center justify-center gap-2">
                <Sparkles className="w-4 h-4 text-emerald-400" />
                Intelligent AI-Powered Biology Textbook Assistant
                <Zap className="w-4 h-4 text-yellow-400" />
              </p>
              <p className="text-xs text-gray-500 mt-2">
                Powered by RAG • Class 11 Biology • Advanced Search & Analysis
              </p>
            </div>
          </div>

          {/* Main Chat Container */}
          <div className="glass-morphism rounded-2xl shadow-2xl overflow-hidden flex flex-col h-[80vh] border-2 border-emerald-500/20">
            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth">
              {messages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center space-y-8">
                  {/* Icon Animation */}
                  <div className="space-y-4">
                    <div className="flex gap-4 justify-center">
                      <div className="text-emerald-400 animate-bounce-subtle">
                        <Dna className="w-16 h-16 animate-dna" />
                      </div>
                      <div className="text-cyan-400 animate-bounce-subtle delay-100">
                        <Beaker className="w-16 h-16 animate-dna" />
                      </div>
                      <div className="text-purple-400 animate-bounce-subtle delay-200">
                        <Microscope className="w-16 h-16 animate-dna" />
                      </div>
                    </div>
                  </div>

                  <div>
                    <h2 className="text-2xl font-bold text-white mb-2">
                      Welcome to Biology Scholar
                    </h2>
                    <p className="text-gray-400 max-w-md">
                      Ask questions about your Class 11 Biology textbook and get
                      instant, detailed answers with citations.
                    </p>
                  </div>

                  {/* Suggestion Cards */}
                  <div className="w-full max-w-2xl grid grid-cols-2 gap-4">
                    <SuggestionCard
                      icon={<Dna className="w-5 h-5" />}
                      title="Chromosomes"
                      description="Learn about chromosome structure and function"
                      onClick={() =>
                        handleSuggestion(
                          "Explain the structure and function of chromosomes"
                        )
                      }
                    />
                    <SuggestionCard
                      icon={<Beaker className="w-5 h-5" />}
                      title="Enzymes"
                      description="Understand enzyme classification and kinetics"
                      onClick={() =>
                        handleSuggestion(
                          "What are enzymes and how do they work?"
                        )
                      }
                    />
                    <SuggestionCard
                      icon={<TrendingUp className="w-5 h-5" />}
                      title="Photosynthesis"
                      description="Explore the light and dark reactions"
                      onClick={() =>
                        handleSuggestion(
                          "Explain the process of photosynthesis step by step"
                        )
                      }
                    />
                    <SuggestionCard
                      icon={<Microscope className="w-5 h-5" />}
                      title="Cell Structure"
                      description="Learn about organelles and their functions"
                      onClick={() =>
                        handleSuggestion(
                          "What is the structure and function of mitochondria?"
                        )
                      }
                    />
                  </div>
                </div>
              ) : (
                <>
                  {messages.map((msg, index) => (
                    <div
                      key={index}
                      className={`flex gap-4 animate-slide-in-${
                        msg.role === "user" ? "right" : "left"
                      }`}
                    >
                      {/* Avatar */}
                      {msg.role === "bot" && (
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center shrink-0 animate-pulse-glow">
                          <Microscope className="w-5 h-5 text-white" />
                        </div>
                      )}

                      {/* Message Bubble */}
                      <div
                        className={`max-w-[85%] rounded-2xl p-6 ${
                          msg.role === "user"
                            ? "bg-gradient-to-r from-emerald-600 to-cyan-600 text-white rounded-br-none glass-morphism"
                            : "bg-gradient-to-br from-gray-800 to-gray-900 border border-emerald-500/30 text-gray-100 rounded-bl-none"
                        }`}
                      >
                        {msg.role === "bot" ? (
                          <div className="prose prose-invert max-w-none text-sm">
                            <ReactMarkdown
                              urlTransform={customUrlTransform}
                              components={MarkdownComponents as Components}
                            >
                              {msg.text}
                            </ReactMarkdown>
                          </div>
                        ) : (
                          <p className="text-sm leading-relaxed">{msg.text}</p>
                        )}

                        {/* Sources Section */}
                        {msg.sources && msg.sources.length > 0 && (
                          <div className="mt-4 pt-4 border-t border-gray-700">
                            <button
                              onClick={() =>
                                setExpandedSources(
                                  expandedSources === index ? null : index
                                )
                              }
                              className="flex items-center gap-2 text-xs font-semibold text-emerald-400 hover:text-emerald-300 transition-colors uppercase tracking-wider"
                            >
                              <Sparkles className="w-4 h-4" />
                              Sources ({msg.sources.length})
                              <ChevronDown
                                className={`w-3 h-3 transition-transform ${
                                  expandedSources === index ? "rotate-180" : ""
                                }`}
                              />
                            </button>

                            {expandedSources === index && (
                              <div className="mt-3 space-y-2 bg-gray-900/50 rounded-lg p-3">
                                {msg.sources.map((source, i) => (
                                  <SourceCard
                                    key={i}
                                    source={source}
                                    index={i}
                                  />
                                ))}
                              </div>
                            )}
                          </div>
                        )}
                      </div>

                      {msg.role === "user" && (
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gray-700 to-gray-600 flex items-center justify-center shrink-0">
                          <User className="w-5 h-5 text-gray-300" />
                        </div>
                      )}
                    </div>
                  ))}

                  {loading && <LoadingAnimation />}

                  <div ref={messagesEndRef} />
                </>
              )}
            </div>

            {/* Input Area */}
            <form
              onSubmit={handleAsk}
              className="p-6 bg-gradient-to-t from-gray-900 to-gray-800/50 border-t border-emerald-500/20"
            >
              <div className="relative flex items-center gap-2">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ask about cells, photosynthesis, DNA, evolution..."
                  className="flex-1 bg-gray-800/80 border-2 border-emerald-500/30 focus:border-emerald-500 text-gray-100 rounded-2xl pl-6 pr-14 py-4 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all placeholder-gray-500 backdrop-blur-sm"
                  disabled={loading}
                />
                <button
                  type="submit"
                  disabled={loading}
                  className="absolute right-2 p-3 bg-gradient-to-r from-emerald-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 rounded-xl transition-all transform hover:scale-110 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
                >
                  {loading ? (
                    <Loader className="w-5 h-5 text-white animate-spin" />
                  ) : (
                    <Send className="w-5 h-5 text-white" />
                  )}
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-2 ml-2">
              </p>
            </form>
          </div>

          {/* Footer */}
          <div className="mt-4 text-center text-xs text-gray-600">
            <p>
              Biology Scholar © 2026 • Advanced RAG Technology • Learn Better,
              Faster
            </p>
          </div>
        </div>
      </div>
    </>
  );
}

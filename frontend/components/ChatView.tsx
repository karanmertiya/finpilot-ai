'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  Sparkles,
  Bot,
  User as UserIcon,
  FileText,
  Wrench,
  Clock,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  PlusCircle,
  Trash2,
  HelpCircle,
  Copy,
  Check
} from 'lucide-react';
import { api } from '@/lib/api';
import { ChatMessage, CitationRecord, ToolCallRecord } from '@/lib/types';

export const ChatView: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const [expandedTools, setExpandedTools] = useState<Record<string, boolean>>({});
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestedQueries = [
    "Calculate EMI for a 20 lakh home loan at 8.5% for 20 years",
    "What are the prepayment charges mentioned in my loan agreement document?",
    "Which categories have exceeded their monthly budget limit?",
    "Are there any unusual or suspicious transactions flagged in my account?",
    "How much did I spend in total on Housing & Rent vs Groceries?"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (textToSend?: string) => {
    const query = textToSend || input;
    if (!query.trim() || loading) return;

    const userMessage: ChatMessage = {
      id: `temp-${Date.now()}`,
      conversation_id: conversationId || '',
      sender: 'user',
      content: query,
      created_at: new Date().toISOString()
    };

    setMessages((prev) => [...prev, userMessage]);
    if (!textToSend) setInput('');
    setLoading(true);

    try {
      const resp = await api.sendChatMessage(query, conversationId);
      if (!conversationId && resp.conversation_id) {
        setConversationId(resp.conversation_id);
      }

      const assistantMessage: ChatMessage = {
        id: resp.message_id || `asst-${Date.now()}`,
        conversation_id: resp.conversation_id,
        sender: 'assistant',
        content: resp.content,
        tool_calls: resp.tool_calls,
        citations: resp.citations,
        chart_data: resp.chart_data,
        created_at: new Date().toISOString()
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      const errorMessage: ChatMessage = {
        id: `err-${Date.now()}`,
        conversation_id: conversationId || '',
        sender: 'assistant',
        content: `⚠️ Failed to process request: ${err.message || 'Server error'}. Please verify backend connection.`,
        created_at: new Date().toISOString()
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const toggleToolExpand = (msgId: string) => {
    setExpandedTools((prev) => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const startNewChat = () => {
    setMessages([]);
    setConversationId(undefined);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-130px)] rounded-2xl bg-[#0a0f1c] border border-slate-800 overflow-hidden shadow-2xl">
      {/* Header */}
      <div className="px-6 py-3.5 border-b border-slate-800 bg-[#0e1626] flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-teal-500/10 border border-teal-500/30 text-teal-300">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <span>FinPilot Copilot</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-teal-950 text-teal-300 border border-teal-800">
                Grounding & Tool Calling Active
              </span>
            </h2>
            <p className="text-xs text-slate-400">Natural language personal financial intelligence & document Q&A</p>
          </div>
        </div>

        <button
          onClick={startNewChat}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-all"
        >
          <PlusCircle className="w-3.5 h-3.5" />
          <span>New Chat</span>
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="max-w-2xl mx-auto py-8 text-center space-y-6">
            <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-tr from-teal-500/20 to-emerald-500/20 border border-teal-500/30 flex items-center justify-center text-teal-300 shadow-xl">
              <Sparkles className="w-7 h-7" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">How can I assist your finances today?</h3>
              <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                Ask about spending analytics, loan EMI calculations, document clauses from your loan agreement, or budget optimization.
              </p>
            </div>

            {/* Suggested Chips */}
            <div className="space-y-2 text-left">
              <span className="text-xs font-semibold text-slate-400 flex items-center gap-1 px-1">
                <HelpCircle className="w-3.5 h-3.5" /> Suggested Queries
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {suggestedQueries.map((sq, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(sq)}
                    className="p-3 text-left rounded-xl bg-slate-900/80 hover:bg-slate-800/80 border border-slate-800 text-xs text-slate-300 hover:text-white transition-all hover:border-teal-500/40 shadow-sm"
                  >
                    "{sq}"
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3.5 max-w-3xl ${
                msg.sender === 'user' ? 'ml-auto flex-row-reverse' : 'mr-auto'
              }`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-xl flex items-center justify-center text-xs shrink-0 ${
                  msg.sender === 'user'
                    ? 'bg-teal-600 text-white shadow-md'
                    : 'bg-slate-800 border border-slate-700 text-teal-400'
                }`}
              >
                {msg.sender === 'user' ? <UserIcon className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              {/* Message Content Container */}
              <div className="space-y-2 w-full">
                <div
                  className={`p-4 rounded-2xl text-xs leading-relaxed shadow-md ${
                    msg.sender === 'user'
                      ? 'bg-teal-600 text-white rounded-tr-none'
                      : 'bg-[#0f182a] border border-[#1e2c45] text-slate-200 rounded-tl-none'
                  }`}
                >
                  <div className="whitespace-pre-wrap font-sans text-xs">{msg.content}</div>

                  {/* Copy Button */}
                  {msg.sender === 'assistant' && (
                    <div className="flex justify-end mt-2 pt-2 border-t border-slate-800/80">
                      <button
                        onClick={() => handleCopy(msg.id, msg.content)}
                        className="text-[10px] text-slate-400 hover:text-teal-300 flex items-center gap-1 transition-colors"
                      >
                        {copiedId === msg.id ? (
                          <>
                            <Check className="w-3 h-3 text-emerald-400" />
                            <span className="text-emerald-400">Copied</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3 h-3" />
                            <span>Copy</span>
                          </>
                        )}
                      </button>
                    </div>
                  )}
                </div>

                {/* Citations Box (if grounded in document RAG) */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="p-3 rounded-xl bg-[#091524] border border-teal-800/50 space-y-2 text-xs">
                    <div className="flex items-center gap-1.5 text-teal-400 font-semibold text-[11px]">
                      <FileText className="w-3.5 h-3.5" />
                      <span>Retrieved Document Evidence ({msg.citations.length} passage)</span>
                    </div>
                    {msg.citations.map((c, i) => (
                      <div key={i} className="p-2 rounded-lg bg-slate-900/90 border border-slate-800 text-[11px]">
                        <div className="flex items-center justify-between text-slate-400 mb-1">
                          <strong className="text-slate-200">{c.filename}</strong>
                          <span className="text-[10px] font-mono">Page {c.page_number || 1} • Similarity: {(c.similarity_score * 100).toFixed(1)}%</span>
                        </div>
                        <p className="text-slate-300 italic line-clamp-3">"{c.passage}"</p>
                      </div>
                    ))}
                  </div>
                )}

                {/* Tool Execution Inspector (Transparency) */}
                {msg.tool_calls && msg.tool_calls.length > 0 && (
                  <div className="rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden text-xs">
                    <button
                      onClick={() => toggleToolExpand(msg.id)}
                      className="w-full px-3 py-2 flex items-center justify-between text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 text-[11px] font-medium"
                    >
                      <div className="flex items-center gap-1.5">
                        <Wrench className="w-3.5 h-3.5 text-teal-400" />
                        <span>Tool Provenance: <strong className="text-slate-200">{msg.tool_calls.map(t => t.tool_name).join(', ')}</strong></span>
                      </div>
                      {expandedTools[msg.id] ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </button>

                    {expandedTools[msg.id] && (
                      <div className="p-3 border-t border-slate-800 bg-[#090e17] space-y-2">
                        {msg.tool_calls.map((tc, idx) => (
                          <div key={idx} className="space-y-1">
                            <div className="flex items-center justify-between text-[10px] text-slate-400">
                              <span className="font-mono text-teal-400">{tc.tool_name}()</span>
                              <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {tc.execution_time_ms}ms</span>
                            </div>
                            <pre className="p-2 rounded bg-slate-950 font-mono text-[10px] text-slate-300 overflow-x-auto border border-slate-900">
                              {JSON.stringify(tc.arguments, null, 2)}
                            </pre>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {loading && (
          <div className="flex items-center gap-3 text-slate-400 text-xs py-2">
            <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-teal-400 animate-spin">
              <Bot className="w-4 h-4" />
            </div>
            <div className="flex items-center gap-2">
              <span className="animate-pulse">Consulting verified records & tools...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <div className="p-4 border-t border-slate-800 bg-[#0e1626]">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-3"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about spending, loan EMIs, budget limits, or document clauses..."
            className="flex-1 bg-slate-900 border border-slate-700/80 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-teal-500 transition-colors"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="px-4 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-500 disabled:opacity-50 text-white text-xs font-semibold flex items-center gap-1.5 transition-all shadow-md active:scale-95"
          >
            <span>Send</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </div>
  );
};

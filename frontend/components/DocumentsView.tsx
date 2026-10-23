'use client';

import React, { useState, useEffect } from 'react';
import {
  FileText,
  UploadCloud,
  Trash2,
  Eye,
  CheckCircle2,
  Clock,
  AlertCircle,
  FileCheck,
  X,
  Layers
} from 'lucide-react';
import { api } from '@/lib/api';
import { DocumentItem } from '@/lib/types';

export const DocumentsView: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [selectedDoc, setSelectedDoc] = useState<DocumentItem | null>(null);

  const fetchDocs = async () => {
    setLoading(true);
    try {
      const data = await api.listDocuments();
      setDocuments(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 10 * 1024 * 1024) {
      setUploadError('File exceeds 10MB upload limit.');
      return;
    }

    setUploadLoading(true);
    setUploadError(null);
    try {
      await api.uploadDocument(file);
      fetchDocs();
    } catch (err: any) {
      setUploadError(err.message || 'Failed to upload document');
    } finally {
      setUploadLoading(false);
      e.target.value = '';
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this document and purge its vector embeddings?')) return;
    try {
      await api.deleteDocument(id);
      fetchDocs();
      if (selectedDoc?.id === id) setSelectedDoc(null);
    } catch (err) {
      console.error(err);
    }
  };

  const handleInspect = async (id: string) => {
    try {
      const doc = await api.getDocument(id);
      setSelectedDoc(doc);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-5 rounded-2xl bg-[#0f182a] border border-[#1e2c45]">
        <div>
          <h2 className="text-base font-bold text-white">Financial Document Center & RAG Store</h2>
          <p className="text-xs text-slate-400">Upload bank statements, loan agreements, and policy documents for grounded retrieval</p>
        </div>

        <label className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold cursor-pointer transition-all shadow-md active:scale-95">
          <UploadCloud className="w-4 h-4" />
          <span>{uploadLoading ? 'Indexing Chunks...' : 'Upload Document'}</span>
          <input
            type="file"
            accept=".pdf,.txt,.csv"
            disabled={uploadLoading}
            onChange={handleFileUpload}
            className="hidden"
          />
        </label>
      </div>

      {uploadError && (
        <div className="p-3.5 rounded-xl bg-rose-950/60 border border-rose-800 text-xs text-rose-300 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{uploadError}</span>
        </div>
      )}

      {/* Documents Grid / List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {loading ? (
          <div className="col-span-full py-12 text-center text-slate-400 text-xs">
            Loading indexed documents...
          </div>
        ) : documents.length === 0 ? (
          <div className="col-span-full p-8 rounded-2xl bg-[#0f182a] border border-[#1e2c45] text-center space-y-3">
            <FileText className="w-8 h-8 text-slate-500 mx-auto" />
            <p className="text-xs text-slate-300">No documents uploaded yet.</p>
            <p className="text-[11px] text-slate-500">Upload PDF loan sanctions or bank statements to enable grounded Q&A.</p>
          </div>
        ) : (
          documents.map((doc) => (
            <div
              key={doc.id}
              className="p-5 rounded-2xl bg-[#0f182a] border border-[#1e2c45] flex flex-col justify-between hover:border-slate-700 transition-all space-y-4"
            >
              <div className="space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2.5">
                    <div className="p-2.5 rounded-xl bg-teal-500/10 text-teal-300 border border-teal-500/20">
                      <FileText className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-white line-clamp-1">{doc.filename}</h4>
                      <p className="text-[10px] text-slate-400 uppercase font-mono">
                        {doc.file_type} • {(doc.file_size_bytes / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  </div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800 flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>{doc.status}</span>
                  </span>
                </div>

                <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800/80 flex items-center justify-between text-xs text-slate-300">
                  <span className="flex items-center gap-1.5 text-[11px]">
                    <Layers className="w-3.5 h-3.5 text-teal-400" />
                    <span>Vector Index</span>
                  </span>
                  <span className="font-mono font-semibold text-white">{doc.chunk_count} Chunks</span>
                </div>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-slate-800/80 text-xs">
                <button
                  onClick={() => handleInspect(doc.id)}
                  className="flex items-center gap-1 text-slate-400 hover:text-teal-300 transition-colors"
                >
                  <Eye className="w-3.5 h-3.5" />
                  <span>Inspect Chunks</span>
                </button>

                <button
                  onClick={() => handleDelete(doc.id)}
                  className="text-slate-500 hover:text-rose-400 transition-colors p-1"
                  title="Delete Document"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Chunk Inspector Modal */}
      {selectedDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-2xl max-h-[80vh] flex flex-col rounded-2xl bg-[#0f182a] border border-[#1e2c45] p-6 shadow-2xl relative">
            <button
              onClick={() => setSelectedDoc(null)}
              className="absolute right-4 top-4 text-slate-400 hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
            <h3 className="text-sm font-bold text-white mb-1">Passage Index Inspector</h3>
            <p className="text-xs text-slate-400 mb-4">
              Showing indexed semantic passages for <strong className="text-white">{selectedDoc.filename}</strong>
            </p>

            <div className="flex-1 overflow-y-auto space-y-3 pr-2">
              {selectedDoc.chunks && selectedDoc.chunks.length > 0 ? (
                selectedDoc.chunks.map((c) => (
                  <div key={c.id} className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-xs space-y-1.5">
                    <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono">
                      <span>Chunk #{c.chunk_index + 1}</span>
                      <span>Page {c.page_number || 1}</span>
                    </div>
                    <p className="text-slate-300 leading-relaxed font-sans text-xs">
                      "{c.content}"
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-400 text-center py-6">No chunks found for this document.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

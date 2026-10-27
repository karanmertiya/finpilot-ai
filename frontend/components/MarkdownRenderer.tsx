'use client';

import React from 'react';

interface MarkdownRendererProps {
  content: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  if (!content) return null;

  // Helper to render inline markdown: **bold**, *italic*, `code`, links
  const renderInline = (text: string): React.ReactNode => {
    if (!text) return null;

    const parts: React.ReactNode[] = [];
    // Match complete **bold**, trailing **unclosed, `code`, *italic*, and URLs
    const regex = /(\*\*.*?\*\*|\*\*[^*\n]+$|`.*?`|\*[^*\n]+?\*|https?:\/\/[^\s]+)/g;
    let lastIndex = 0;
    let match: RegExpExecArray | null;

    while ((match = regex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        parts.push(text.substring(lastIndex, match.index));
      }

      const token = match[0];
      if (token.startsWith('**')) {
        const inner = token.endsWith('**') && token.length >= 4 ? token.slice(2, -2) : token.slice(2);
        parts.push(
          <strong key={match.index} className="font-semibold text-white">
            {renderInline(inner)}
          </strong>
        );
      } else if (token.startsWith('`') && token.endsWith('`')) {
        const inner = token.slice(1, -1);
        parts.push(
          <code
            key={match.index}
            className="px-1.5 py-0.5 mx-0.5 rounded bg-slate-800 text-teal-300 font-mono text-[11px] border border-slate-700/60"
          >
            {inner}
          </code>
        );
      } else if (token.startsWith('*') && token.endsWith('*')) {
        const inner = token.slice(1, -1);
        parts.push(
          <em key={match.index} className="italic text-slate-300">
            {renderInline(inner)}
          </em>
        );
      } else if (token.startsWith('http')) {
        parts.push(
          <a
            key={match.index}
            href={token}
            target="_blank"
            rel="noopener noreferrer"
            className="text-teal-400 hover:text-teal-300 underline underline-offset-2"
          >
            {token}
          </a>
        );
      }

      lastIndex = regex.lastIndex;
    }

    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex));
    }

    return parts.length === 1 ? parts[0] : <>{parts}</>;
  };

  // Parse lines into high-level blocks
  const lines = content.split('\n');
  const blocks: React.ReactNode[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];
    const trimmed = line.trim();

    // 1. Empty lines
    if (!trimmed) {
      blocks.push(<div key={`empty-${i}`} className="h-2" />);
      i++;
      continue;
    }

    // 2. Code Block (```)
    if (trimmed.startsWith('```')) {
      const lang = trimmed.slice(3).trim();
      const codeLines: string[] = [];
      i++;
      while (i < lines.length && !lines[i].trim().startsWith('```')) {
        codeLines.push(lines[i]);
        i++;
      }
      i++; // skip closing ```
      blocks.push(
        <div key={`code-${i}`} className="my-2.5 rounded-xl overflow-hidden border border-slate-800 bg-slate-950/90 shadow-md">
          {lang && (
            <div className="px-3 py-1.5 bg-slate-900 border-b border-slate-800 text-[10px] font-mono text-slate-400 uppercase tracking-wider">
              {lang}
            </div>
          )}
          <pre className="p-3 text-[11px] font-mono text-teal-300 overflow-x-auto leading-relaxed">
            <code>{codeLines.join('\n')}</code>
          </pre>
        </div>
      );
      continue;
    }

    // 3. Table Block (| ... |)
    if (trimmed.startsWith('|')) {
      const tableLines: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith('|')) {
        tableLines.push(lines[i].trim());
        i++;
      }

      if (tableLines.length >= 2) {
        // Parse header
        let headerCols = tableLines[0].split('|').map((c) => c.trim());
        if (headerCols.length > 0 && headerCols[0] === '') headerCols.shift();
        if (headerCols.length > 0 && headerCols[headerCols.length - 1] === '') headerCols.pop();
        
        // Check if row 1 is separator (e.g. :--- | ---:)
        const hasSeparator = /^[:\-\s\|]+$/.test(tableLines[1]);
        const startRow = hasSeparator ? 2 : 1;
        const bodyRows = tableLines.slice(startRow).map((rowStr) => {
          let cells = rowStr.split('|').map((c) => c.trim());
          if (cells.length > 0 && cells[0] === '') cells.shift();
          if (cells.length > 0 && cells[cells.length - 1] === '') cells.pop();
          while (cells.length < headerCols.length) cells.push('');
          return cells.slice(0, headerCols.length);
        });

        blocks.push(
          <div key={`table-${i}`} className="overflow-x-auto my-3 rounded-xl border border-slate-800 bg-slate-900/60 shadow-sm">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-700/60 bg-slate-800/60">
                  {headerCols.map((col, idx) => (
                    <th key={idx} className="px-3.5 py-2 font-semibold text-teal-300 uppercase tracking-wider text-[11px]">
                      {renderInline(col)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {bodyRows.map((row, rIdx) => (
                  <tr key={rIdx} className="hover:bg-slate-800/30 transition-colors">
                    {row.map((cell, cIdx) => (
                      <td key={cIdx} className="px-3.5 py-2 text-slate-200">
                        {renderInline(cell)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
        continue;
      }
    }

    // 4. Headers (#, ##, ###, ####)
    if (trimmed.startsWith('#')) {
      const match = trimmed.match(/^(#{1,6})\s+(.*)$/);
      if (match) {
        const level = match[1].length;
        const title = match[2];
        if (level === 1) {
          blocks.push(
            <h1 key={`h1-${i}`} className="text-base font-bold text-white mt-4 mb-2">
              {renderInline(title)}
            </h1>
          );
        } else if (level === 2) {
          blocks.push(
            <h2 key={`h2-${i}`} className="text-sm font-bold text-teal-300 mt-3 mb-1.5 flex items-center gap-1.5">
              {renderInline(title)}
            </h2>
          );
        } else if (level === 3) {
          blocks.push(
            <h3 key={`h3-${i}`} className="text-xs font-bold text-slate-100 mt-3 mb-1 uppercase tracking-wider border-b border-slate-800/80 pb-1">
              {renderInline(title)}
            </h3>
          );
        } else {
          blocks.push(
            <h4 key={`h4-${i}`} className="text-xs font-semibold text-slate-300 mt-2 mb-1">
              {renderInline(title)}
            </h4>
          );
        }
        i++;
        continue;
      }
    }

    // 5. Blockquote (>)
    if (trimmed.startsWith('>')) {
      const quoteText = trimmed.replace(/^>\s*/, '');
      blocks.push(
        <blockquote
          key={`quote-${i}`}
          className="border-l-2 border-teal-500 bg-teal-500/10 px-3.5 py-2 my-2 rounded-r-lg text-slate-300 italic text-xs leading-relaxed"
        >
          {renderInline(quoteText)}
        </blockquote>
      );
      i++;
      continue;
    }

    // 6. Unordered Lists (*, -, +)
    if (/^[\*\-\+]\s+/.test(trimmed)) {
      const listItems: string[] = [];
      while (i < lines.length && /^[\*\-\+]\s+/.test(lines[i].trim())) {
        listItems.push(lines[i].trim().replace(/^[\*\-\+]\s+/, ''));
        i++;
      }
      blocks.push(
        <ul key={`ul-${i}`} className="space-y-1.5 my-2 pl-1">
          {listItems.map((item, idx) => (
            <li key={idx} className="flex items-start gap-2 text-xs leading-relaxed text-slate-200">
              <span className="w-1.5 h-1.5 rounded-full bg-teal-400 mt-1.5 shrink-0" />
              <div className="flex-1">{renderInline(item)}</div>
            </li>
          ))}
        </ul>
      );
      continue;
    }

    // 7. Ordered Lists (1. , 2. )
    if (/^\d+\.\s+/.test(trimmed)) {
      const listItems: { num: string; text: string }[] = [];
      while (i < lines.length && /^\d+\.\s+/.test(lines[i].trim())) {
        const m = lines[i].trim().match(/^(\d+)\.\s+(.*)$/);
        if (m) {
          listItems.push({ num: m[1], text: m[2] });
        }
        i++;
      }
      blocks.push(
        <ol key={`ol-${i}`} className="space-y-1.5 my-2 pl-1">
          {listItems.map((item, idx) => (
            <li key={idx} className="flex items-start gap-2 text-xs leading-relaxed text-slate-200">
              <span className="text-teal-400 font-bold shrink-0 text-[11px] min-w-[16px]">{item.num}.</span>
              <div className="flex-1">{renderInline(item.text)}</div>
            </li>
          ))}
        </ol>
      );
      continue;
    }

    // 8. Standard Paragraph
    blocks.push(
      <p key={`p-${i}`} className="text-xs text-slate-200 leading-relaxed my-1.5">
        {renderInline(trimmed)}
      </p>
    );
    i++;
  }

  return <div className="space-y-1 text-xs text-slate-200">{blocks}</div>;
};

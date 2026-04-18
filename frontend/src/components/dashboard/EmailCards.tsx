import { useState } from 'react';
import { ChevronDown, ChevronUp, Copy, Check } from 'lucide-react';
import { GeneratedEmail } from '../../types';

interface EmailCardsProps {
  emails: GeneratedEmail[];
  visible: boolean;
}

export default function EmailCards({ emails, visible }: EmailCardsProps) {
  return (
    <div
      className={`bg-white border border-gray-200 rounded-xl shadow-sm transition-all duration-500 ${
        visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
      }`}
    >
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-sm font-semibold text-gray-900">Generated Emails</h3>
        <p className="text-xs text-gray-500 mt-0.5">{emails.length} emails ready to send</p>
      </div>
      <div className="divide-y divide-gray-50">
        {emails.map((email, idx) => (
          <EmailCard
            key={email.id}
            email={email}
            defaultOpen={idx === 0}
            delay={idx * 80}
            visible={visible}
          />
        ))}
      </div>
    </div>
  );
}

interface EmailCardProps {
  email: GeneratedEmail;
  defaultOpen: boolean;
  delay: number;
  visible: boolean;
}

function EmailCard({ email, defaultOpen, delay, visible }: EmailCardProps) {
  const [open, setOpen] = useState(defaultOpen);
  const [copied, setCopied] = useState(false);

  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(`Subject: ${email.subject}\n\n${email.body}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={`transition-all duration-300 ${visible ? 'opacity-100' : 'opacity-0'}`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      <div
        onClick={() => setOpen(!open)}
        className="w-full text-left px-6 py-4 flex items-start justify-between gap-3 hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-start gap-3 min-w-0">
          <div className="w-7 h-7 rounded-md bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center text-xs font-bold text-blue-700 flex-shrink-0 mt-0.5">
            {email.company[0]}
          </div>
          <div className="min-w-0">
            <p className="text-xs font-medium text-gray-500 mb-0.5">{email.company}</p>
            <p className="text-sm font-semibold text-gray-900 truncate">{email.subject}</p>
          </div>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          {open && (
            <button
              onClick={handleCopy}
              className="inline-flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700 bg-gray-100 hover:bg-gray-200 px-2 py-1 rounded-md transition-colors"
            >
              {copied ? <Check size={11} className="text-emerald-600" /> : <Copy size={11} />}
              {copied ? 'Copied' : 'Copy'}
            </button>
          )}
          {open ? (
            <ChevronUp size={15} className="text-gray-400" />
          ) : (
            <ChevronDown size={15} className="text-gray-400" />
          )}
        </div>
      </div>

      {open && (
        <div className="px-6 pb-5">
          <div className="bg-gray-50 border border-gray-100 rounded-lg p-4">
            <pre className="text-xs text-gray-700 whitespace-pre-wrap leading-relaxed font-sans">
              {email.body}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}

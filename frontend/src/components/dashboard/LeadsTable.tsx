import { ExternalLink, Send, ChevronDown } from 'lucide-react';
import { Lead, LeadStatus } from '../../types';

interface LeadsTableProps {
  leads: Lead[];
  visible: boolean;
}

export default function LeadsTable({ leads, visible }: LeadsTableProps) {
  return (
    <div
      className={`bg-white border border-gray-200 rounded-xl shadow-sm transition-all duration-500 ${
        visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
      }`}
    >
      <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900">Discovered Leads</h3>
          <p className="text-xs text-gray-500 mt-0.5">{leads.length} contacts found</p>
        </div>
        <button className="flex items-center gap-1.5 text-xs font-medium text-gray-600 border border-gray-200 px-3 py-1.5 rounded-lg hover:bg-gray-50 transition-colors">
          Filter
          <ChevronDown size={12} />
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-100">
              <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide px-6 py-3">
                Company
              </th>
              <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide px-4 py-3">
                Source
              </th>
              <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide px-4 py-3">
                Status
              </th>
              <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wide px-4 py-3">
                Action
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {leads.map((lead, idx) => (
              <tr
                key={lead.id}
                className={`hover:bg-gray-50 transition-all duration-300 ${
                  visible ? 'opacity-100' : 'opacity-0'
                }`}
                style={{ transitionDelay: `${idx * 50}ms` }}
              >
                <td className="px-6 py-3.5">
                  <div className="flex items-center gap-3">
                    <div className="w-7 h-7 rounded-md bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center text-xs font-bold text-gray-600 flex-shrink-0">
                      {lead.company[0]}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 text-sm">{lead.company}</p>
                      {lead.email && (
                        <p className="text-xs text-gray-400">{lead.email}</p>
                      )}
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3.5">
                  <span className="text-sm text-gray-600">{lead.source}</span>
                </td>
                <td className="px-4 py-3.5">
                  <StatusPill status={lead.status} />
                </td>
                <td className="px-4 py-3.5">
                  <div className="flex items-center gap-2">
                    <button className="inline-flex items-center gap-1.5 text-xs font-medium text-blue-700 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-2.5 py-1.5 rounded-lg transition-colors">
                      <Send size={11} />
                      Send
                    </button>
                    <button className="inline-flex items-center gap-1 text-xs font-medium text-gray-500 hover:text-gray-700 hover:bg-gray-100 px-2 py-1.5 rounded-lg transition-colors">
                      <ExternalLink size={11} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StatusPill({ status }: { status: LeadStatus }) {
  const styles: Record<LeadStatus, string> = {
    New: 'bg-blue-50 text-blue-700 border-blue-100',
    Pending: 'bg-amber-50 text-amber-700 border-amber-100',
    Sent: 'bg-emerald-50 text-emerald-700 border-emerald-100',
  };

  const dots: Record<LeadStatus, string> = {
    New: 'bg-blue-500',
    Pending: 'bg-amber-500',
    Sent: 'bg-emerald-500',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${styles[status]}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dots[status]}`}></span>
      {status}
    </span>
  );
}

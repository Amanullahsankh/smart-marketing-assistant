import { useState, useEffect } from 'react';
import { CRMLead } from '../types';
import { Download, Users, Mail, Building, Calendar, AlertCircle, Clock, CheckCircle2, Filter } from 'lucide-react';

const API_BASE_URL = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000').replace(/\/$/, '');

interface Campaign {
  id: string;
  company_input: string;
  created_at: string;
}

export function exportToCSV(data: any[]): void {
  if (!data || data.length === 0) {
    alert("No data available to export.");
    return;
  }

  const escapeCSV = (value: any) => {
    if (value === null || value === undefined) return '""';
    const strValue = String(value);
    if (strValue.includes(',') || strValue.includes('"') || strValue.includes('\n')) {
      return `"${strValue.replace(/"/g, '""')}"`;
    }
    return strValue;
  };

  const headers = Object.keys(data[0]);
  const csvRows = [];
  csvRows.push(headers.map(escapeCSV).join(','));

  for (const row of data) {
    const values = headers.map(header => escapeCSV(row[header]));
    csvRows.push(values.join(','));
  }

  const csvString = csvRows.join('\n');
  const blob = new Blob(["\uFEFF" + csvString], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  
  const link = document.createElement("a");
  link.href = url;
  link.download = "leads.csv";
  link.style.display = "none";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export default function CRMDashboard() {
  const [leads, setLeads] = useState<CRMLead[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [selectedCampaign, setSelectedCampaign] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCampaigns();
  }, []);

  useEffect(() => {
    fetchLeads(selectedCampaign);
  }, [selectedCampaign]);

  const fetchCampaigns = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/campaigns`);
      if (response.ok) {
        const data = await response.json();
        setCampaigns(data);
      }
    } catch (err) {
      console.error("Failed to fetch campaigns", err);
    }
  };

  const fetchLeads = async (campaignId: string) => {
    try {
      setLoading(true);
      const url = campaignId 
        ? `${API_BASE_URL}/leads?campaign_id=${campaignId}` 
        : `${API_BASE_URL}/leads`;
        
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch leads');
      const data = await response.json();
      
      // Calculate dynamic status based on date
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      const mappedLeads = data.map((lead: CRMLead) => {
        if (!lead.next_followup_date) return lead; // Safe guard for old data
        const followUpDate = new Date(lead.next_followup_date);
        followUpDate.setHours(0, 0, 0, 0);
        
        if (today >= followUpDate && lead.status !== 'Completed') {
          return { ...lead, status: 'Follow-up Due' };
        }
        return lead;
      });

      setLeads(mappedLeads);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    if (status === 'Follow-up Due') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-red-50 text-red-700 border border-red-200">
          <AlertCircle size={12} /> Follow-up Due
        </span>
      );
    }
    if (status === 'Completed') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-green-50 text-green-700 border border-green-200">
          <CheckCircle2 size={12} /> Completed
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200">
        <Clock size={12} /> {status}
      </span>
    );
  };

  // Removed internal exportToCSV

  return (
    <div className="max-w-screen-xl mx-auto px-6 py-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Users className="text-blue-600" />
            CRM Dashboard
          </h1>
          <p className="text-gray-500 mt-1 text-sm">Manage your AI-generated leads and follow-ups</p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="relative">
            <Filter size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <select
              value={selectedCampaign}
              onChange={(e) => setSelectedCampaign(e.target.value)}
              className="pl-8 pr-8 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none shadow-sm cursor-pointer"
            >
              <option value="">All Campaigns</option>
              {campaigns.map(c => (
                <option key={c.id} value={c.id}>
                  {c.company_input.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0] || c.id}
                </option>
              ))}
            </select>
            {/* Custom arrow for select */}
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-500">
              <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
              </svg>
            </div>
          </div>
          
          <button 
            onClick={() => exportToCSV(leads)}
            disabled={leads.length === 0 || loading}
            className="inline-flex items-center gap-2 bg-white border border-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm font-semibold hover:bg-gray-50 transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download size={16} />
            Export CSV
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-gray-50 text-gray-500 font-medium border-b border-gray-200">
              <tr>
                <th className="px-6 py-4">Lead Email</th>
                <th className="px-6 py-4">Company Name</th>
                <th className="px-6 py-4">Persona</th>
                <th className="px-6 py-4">Last Action</th>
                <th className="px-6 py-4">Next Follow-up Date</th>
                <th className="px-6 py-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                    <div className="flex flex-col items-center gap-3">
                      <div className="w-8 h-8 border-4 border-blue-100 border-t-blue-600 rounded-full animate-spin"></div>
                      <p>Loading CRM data...</p>
                    </div>
                  </td>
                </tr>
              ) : error ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-red-500">
                    <AlertCircle className="mx-auto mb-2 opacity-50" size={32} />
                    {error}
                  </td>
                </tr>
              ) : leads.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                    <Users className="mx-auto mb-2 opacity-20" size={32} />
                    No leads found. Run a campaign to generate leads!
                  </td>
                </tr>
              ) : (
                leads.map((lead) => (
                  <tr key={lead.id} className="hover:bg-gray-50 transition-colors group">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 text-gray-900 font-medium">
                        <Mail size={14} className="text-gray-400 group-hover:text-blue-500 transition-colors" />
                        {lead.lead_email}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 text-gray-600">
                        <Building size={14} className="text-gray-400" />
                        {lead.company_name}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex px-2 py-1 rounded-md bg-gray-100 text-gray-600 text-xs font-medium">
                        {lead.persona}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-600">
                      {lead.last_action}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 text-gray-600">
                        <Calendar size={14} className="text-gray-400" />
                        {lead.next_followup_date ? new Date(lead.next_followup_date).toLocaleDateString(undefined, { 
                          year: 'numeric', 
                          month: 'short', 
                          day: 'numeric' 
                        }) : 'N/A'}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {getStatusBadge(lead.status)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

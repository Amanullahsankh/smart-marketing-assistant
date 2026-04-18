import { Users, Mail, FolderOpen, Sheet } from 'lucide-react';
import { CampaignMetrics } from '../../types';

interface MetricCardsProps {
  metrics: CampaignMetrics;
  visible: boolean;
}

export default function MetricCards({ metrics, visible }: MetricCardsProps) {
  const cards = [
    {
      label: 'Leads Found',
      value: metrics.leadsFound,
      icon: <Users size={18} />,
      color: 'blue',
      change: '+12 today',
    },
    {
      label: 'Emails Generated',
      value: metrics.emailsGenerated,
      icon: <Mail size={18} />,
      color: 'green',
      change: 'Ready to send',
    },
    {
      label: 'Portfolio',
      value: metrics.portfolio,
      icon: <FolderOpen size={18} />,
      color: 'amber',
      change: 'Uploaded to Drive',
    },
    {
      label: 'Sheet Rows',
      value: metrics.sheetRows,
      icon: <Sheet size={18} />,
      color: 'slate',
      change: 'Google Sheets synced',
    },
  ];

  const colorMap: Record<string, { bg: string; icon: string; text: string }> = {
    blue: { bg: 'bg-blue-50', icon: 'text-blue-600', text: 'text-blue-700' },
    green: { bg: 'bg-emerald-50', icon: 'text-emerald-600', text: 'text-emerald-700' },
    amber: { bg: 'bg-amber-50', icon: 'text-amber-600', text: 'text-amber-700' },
    slate: { bg: 'bg-slate-50', icon: 'text-slate-600', text: 'text-slate-700' },
  };

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, idx) => {
        const colors = colorMap[card.color];
        return (
          <div
            key={card.label}
            className={`bg-white border border-gray-200 rounded-xl p-5 shadow-sm transition-all duration-500 ${
              visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
            }`}
            style={{ transitionDelay: `${idx * 80}ms` }}
          >
            <div className="flex items-center justify-between mb-4">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                {card.label}
              </p>
              <div className={`w-8 h-8 ${colors.bg} rounded-lg flex items-center justify-center ${colors.icon}`}>
                {card.icon}
              </div>
            </div>
            <p className="text-3xl font-bold text-gray-900 tabular-nums">
              {visible ? card.value : 0}
            </p>
            <p className={`text-xs font-medium mt-1.5 ${colors.text}`}>{card.change}</p>
          </div>
        );
      })}
    </div>
  );
}

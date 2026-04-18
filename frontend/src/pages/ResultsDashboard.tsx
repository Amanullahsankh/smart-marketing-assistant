import { useEffect, useState } from 'react';
import { ArrowLeft, Calendar, Globe, Zap } from 'lucide-react';
import PipelineProgress from '../components/pipeline/PipelineProgress';
import MetricCards from '../components/dashboard/MetricCards';
import LeadsTable from '../components/dashboard/LeadsTable';
import EmailCards from '../components/dashboard/EmailCards';
import OutputButtons from '../components/dashboard/OutputButtons';
import { CampaignFormData, PipelineStep } from '../types';

const PIPELINE_LABELS = [
  'Extract Services',
  'Discover Leads',
  'Summarize',
  'Generate Emails',
  'Portfolio',
  'Upload',
];

const STEP_DELAYS_MS = [1200, 2600, 3800, 5200, 6400, 7800];

interface ResultsDashboardProps {
  campaign: CampaignFormData;
  onBack: () => void;
}

export default function ResultsDashboard({ campaign, onBack }: ResultsDashboardProps) {
  const [steps, setSteps] = useState<PipelineStep[]>(
    PIPELINE_LABELS.map((label, idx) => ({ id: idx, label, status: 'idle' }))
  );
  const [dataVisible, setDataVisible] = useState(false);

  useEffect(() => {
    setSteps((prev) =>
      prev.map((s, i) => (i === 0 ? { ...s, status: 'active' } : s))
    );

    STEP_DELAYS_MS.forEach((delay, idx) => {
      const completeTimer = setTimeout(() => {
        setSteps((prev) =>
          prev.map((s, i) => {
            if (i === idx) return { ...s, status: 'complete' };
            if (i === idx + 1) return { ...s, status: 'active' };
            return s;
          })
        );
      }, delay);

      return () => clearTimeout(completeTimer);
    });

    const showDataTimer = setTimeout(() => {
      setDataVisible(true);
    }, STEP_DELAYS_MS[STEP_DELAYS_MS.length - 1] + 600);

    return () => clearTimeout(showDataTimer);
  }, []);

  const allComplete = steps.every((s) => s.status === 'complete');
  const todayStr = new Date().toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });

  const metrics = [
    { label: 'Leads Found', value: campaign.leads?.length ?? 0, sub: 'from website scan' },
    { label: 'Emails Generated', value: campaign.results?.length ?? 0, sub: 'ready to send' },
    { label: 'Portfolio', value: 1, sub: 'PDF created' },
    { label: 'Sheet Rows', value: campaign.results?.length ?? 0, sub: 'logged to Drive' },
  ];

  const leads = (campaign.leads ?? []).map((lead: any, idx: number) => ({
    id: idx,
    company: lead.title ?? 'Unknown',
    website: lead.link ?? '#',
    status: 'new',
    source: 'AI Discovery',
  }));

  const emails = (campaign.results ?? []).map((r: any, idx: number) => ({
    id: idx,
    company: r.client?.title ?? 'Unknown',
    subject: r.email?.subject ?? 'No subject',
    body: r.email?.body ?? 'No body',
  }));

  return (
    <div className="min-h-[calc(100vh-64px)] bg-gray-50">
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-screen-xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={onBack}
                className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-900 transition-colors"
              >
                <ArrowLeft size={15} />
                Campaigns
              </button>
              <span className="text-gray-300">/</span>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-base font-semibold text-gray-900">
                    {campaign.companyName}
                  </h1>
                  <span
                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold ${
                      allComplete
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-100'
                        : 'bg-blue-50 text-blue-700 border border-blue-100'
                    }`}
                  >
                    {allComplete ? (
                      'Complete'
                    ) : (
                      <>
                        <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse"></span>
                        Running
                      </>
                    )}
                  </span>
                </div>
                <div className="flex items-center gap-3 mt-0.5">
                  <span className="flex items-center gap-1 text-xs text-gray-400">
                    <Globe size={11} />
                    {campaign.websiteUrl}
                  </span>
                  <span className="text-gray-200">|</span>
                  <span className="flex items-center gap-1 text-xs text-gray-400">
                    <Zap size={11} />
                    {campaign.scanDepth === 'fast' ? 'Fast Scan' : 'Deep Scan'}
                  </span>
                  <span className="text-gray-200">|</span>
                  <span className="flex items-center gap-1 text-xs text-gray-400">
                    <Calendar size={11} />
                    {todayStr}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-screen-xl mx-auto px-6 py-8 space-y-6">
        <PipelineProgress steps={steps} />

        <MetricCards metrics={metrics} visible={dataVisible} />

        <div className="grid lg:grid-cols-5 gap-6">
          <div className="lg:col-span-3">
            <LeadsTable leads={leads} visible={dataVisible} />
          </div>
          <div className="lg:col-span-2">
            <EmailCards emails={emails} visible={dataVisible} />
          </div>
        </div>

        <div className="flex justify-end">
          <OutputButtons visible={dataVisible} sheetUrl="https://docs.google.com/spreadsheets/d/16MvwG0MAbRhDNJVB34Dhcc9l45hO7qRnkBJLXYJufYQ" />
        </div>
      </div>
    </div>
  );
}

import { useState } from 'react';
import { Zap, Globe, Building2, ArrowRight, CheckCircle2, Shield, BarChart3 } from 'lucide-react';
import { CampaignFormData, ScanDepth } from '../types';

interface HomePageProps {
  onSubmit: (data: CampaignFormData) => void;
}

export default function HomePage({ onSubmit }: HomePageProps) {
  const [companyName, setCompanyName] = useState('');
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [scanDepth, setScanDepth] = useState<ScanDepth>('fast');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{ companyName?: string; websiteUrl?: string }>({});

  const validate = () => {
    const newErrors: { companyName?: string; websiteUrl?: string } = {};
    if (!companyName.trim()) newErrors.companyName = 'Company name is required';
    if (!websiteUrl.trim()) newErrors.websiteUrl = 'Website URL is required';
    else if (!/^https?:\/\/.+/.test(websiteUrl.trim())) {
      newErrors.websiteUrl = 'Please enter a valid URL starting with https://';
    }
    return newErrors;
  };

 const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  const errs = validate();
  if (Object.keys(errs).length > 0) {
    setErrors(errs);
    return;
  }

  setErrors({});
  setLoading(true);

  try {
    const response = await fetch("http://localhost:8000/run-campaign", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        business_name: companyName,
        website_url: websiteUrl,
        page_limit: scanDepth === "fast" ? 2 : 5,
      }),
    });

    const data = await response.json();
    console.log("API Response:", data);

    // 🔥 Send data to next page (dashboard)
    onSubmit({
      companyName,
      websiteUrl,
      scanDepth,
      ...data, // optional if you want backend data
    });

  } catch (error) {
    console.error("Error:", error);
  } finally {
    setLoading(false);
  }
};

  return (
    <div className="min-h-[calc(100vh-64px)] bg-gray-50">
      <div className="max-w-screen-xl mx-auto px-6 py-16">
        <div className="grid lg:grid-cols-2 gap-16 items-start">
          <div className="pt-4">
            <div className="inline-flex items-center gap-2 bg-blue-50 border border-blue-100 text-blue-700 text-xs font-semibold px-3.5 py-1.5 rounded-full mb-6">
              <Zap size={12} />
              AI-Powered B2B Outreach
            </div>
            <h1 className="text-4xl lg:text-5xl font-bold text-gray-900 leading-tight tracking-tight mb-5">
              Turn any website into
              <br />
              <span className="text-blue-700">qualified leads.</span>
            </h1>
            <p className="text-lg text-gray-500 leading-relaxed mb-10 max-w-md">
              Enter a company and URL. Our AI extracts services, discovers prospects, and generates
              personalized outreach emails — in seconds.
            </p>

            <div className="space-y-3 mb-10">
              {[
                'Discovers leads from LinkedIn, websites & directories',
                'Generates personalized email copy with AI',
                'Exports to Google Sheets and Drive automatically',
              ].map((item) => (
                <div key={item} className="flex items-start gap-2.5">
                  <CheckCircle2 size={16} className="text-blue-600 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-gray-600">{item}</span>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-3 gap-6 pt-8 border-t border-gray-200">
              {[
                { label: 'Leads/Hour', value: '200+', icon: <BarChart3 size={16} className="text-blue-600" /> },
                { label: 'Avg Open Rate', value: '42%', icon: <Zap size={16} className="text-blue-600" /> },
                { label: 'Data Sources', value: '12+', icon: <Shield size={16} className="text-blue-600" /> },
              ].map((stat) => (
                <div key={stat.label}>
                  <div className="flex items-center gap-1.5 mb-1">{stat.icon}</div>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{stat.label}</p>
                </div>
              ))}
            </div>
          </div>

          <div>
            <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden">
              <div className="px-8 pt-8 pb-6 border-b border-gray-100">
                <h2 className="text-lg font-semibold text-gray-900">New Campaign</h2>
                <p className="text-sm text-gray-500 mt-1">Set up your target and launch AI analysis</p>
              </div>

              <form onSubmit={handleSubmit} className="p-8 space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Company Name
                  </label>
                  <div className="relative">
                    <Building2
                      size={15}
                      className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400"
                    />
                    <input
                      type="text"
                      value={companyName}
                      onChange={(e) => {
                        setCompanyName(e.target.value);
                        if (errors.companyName) setErrors((p) => ({ ...p, companyName: undefined }));
                      }}
                      placeholder="e.g. Acme Corporation"
                      className={`w-full pl-10 pr-4 py-2.5 text-sm border rounded-lg outline-none transition-colors placeholder-gray-300 ${
                        errors.companyName
                          ? 'border-red-300 focus:border-red-500 focus:ring-2 focus:ring-red-100'
                          : 'border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100'
                      }`}
                    />
                  </div>
                  {errors.companyName && (
                    <p className="text-xs text-red-600 mt-1.5">{errors.companyName}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Website URL
                  </label>
                  <div className="relative">
                    <Globe
                      size={15}
                      className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400"
                    />
                    <input
                      type="text"
                      value={websiteUrl}
                      onChange={(e) => {
                        setWebsiteUrl(e.target.value);
                        if (errors.websiteUrl) setErrors((p) => ({ ...p, websiteUrl: undefined }));
                      }}
                      placeholder="https://acmecorp.com"
                      className={`w-full pl-10 pr-4 py-2.5 text-sm border rounded-lg outline-none transition-colors placeholder-gray-300 ${
                        errors.websiteUrl
                          ? 'border-red-300 focus:border-red-500 focus:ring-2 focus:ring-red-100'
                          : 'border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100'
                      }`}
                    />
                  </div>
                  {errors.websiteUrl && (
                    <p className="text-xs text-red-600 mt-1.5">{errors.websiteUrl}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Scan Depth
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    {(['fast', 'deep'] as ScanDepth[]).map((depth) => (
                      <button
                        key={depth}
                        type="button"
                        onClick={() => setScanDepth(depth)}
                        className={`relative flex flex-col items-start p-4 border-2 rounded-xl text-left transition-all ${
                          scanDepth === depth
                            ? 'border-blue-600 bg-blue-50'
                            : 'border-gray-200 bg-white hover:border-gray-300'
                        }`}
                      >
                        <div className="flex items-center justify-between w-full mb-2">
                          <span
                            className={`text-sm font-semibold capitalize ${
                              scanDepth === depth ? 'text-blue-700' : 'text-gray-800'
                            }`}
                          >
                            {depth}
                          </span>
                          <div
                            className={`w-4 h-4 rounded-full border-2 flex items-center justify-center transition-colors ${
                              scanDepth === depth
                                ? 'border-blue-600 bg-blue-600'
                                : 'border-gray-300'
                            }`}
                          >
                            {scanDepth === depth && (
                              <div className="w-1.5 h-1.5 bg-white rounded-full"></div>
                            )}
                          </div>
                        </div>
                        <span
                          className={`text-xs ${
                            scanDepth === depth ? 'text-blue-600' : 'text-gray-400'
                          }`}
                        >
                          {depth === 'fast' ? '~30 sec · Top-level pages' : '~3 min · Full site crawl'}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex items-center justify-center gap-2 py-3 px-6 bg-blue-700 hover:bg-blue-800 disabled:bg-blue-400 text-white font-semibold text-sm rounded-xl transition-colors shadow-sm shadow-blue-200 mt-2"
                >
                  {loading ? (
                    <>
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                      Launching Campaign...
                    </>
                  ) : (
                    <>
                      Run Campaign
                      <ArrowRight size={16} />
                    </>
                  )}
                </button>

                <p className="text-xs text-center text-gray-400">
                  Campaign results appear instantly in your dashboard
                </p>
              </form>
            </div>

            <div className="mt-4 flex items-center justify-center gap-6">
              {['SOC 2 Compliant', 'GDPR Ready', '256-bit Encryption'].map((label) => (
                <div key={label} className="flex items-center gap-1.5">
                  <Shield size={11} className="text-gray-400" />
                  <span className="text-xs text-gray-400">{label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

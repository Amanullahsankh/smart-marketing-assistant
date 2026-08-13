import { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import ResultsDashboard from './pages/ResultsDashboard';
import CRMDashboard from './pages/CRMDashboard';
import { CampaignFormData } from './types';

type Page = 'home' | 'crm';

export default function App() {
  const [page, setPage] = useState<Page>('home');
  const [campaign, setCampaign] = useState<CampaignFormData | null>(() => {
    const saved = localStorage.getItem("campaignData");
    return saved ? JSON.parse(saved) : null;
  });

  useEffect(() => {
    if (campaign) {
      localStorage.setItem("campaignData", JSON.stringify(campaign));
    } else {
      localStorage.removeItem("campaignData");
    }
  }, [campaign]);

  const handleRunCampaign = (data: CampaignFormData) => {
    setCampaign(data);
    setPage('home');
  };

  const handleNewCampaign = () => {
    setCampaign(null);
    setPage('home');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar 
        onLogoClick={() => setPage('home')} 
        onNavClick={(p) => setPage(p as Page)} 
        activePage={page} 
      />
      
      {page === 'home' && !campaign && (
        <HomePage onSubmit={handleRunCampaign} />
      )}
      
      {page === 'home' && campaign && (
        <ResultsDashboard campaign={campaign} onNewCampaign={handleNewCampaign} />
      )}
      
      {page === 'crm' && <CRMDashboard />}
    </div>
  );
}

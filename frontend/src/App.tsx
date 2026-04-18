import { useState } from 'react';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import ResultsDashboard from './pages/ResultsDashboard';
import { CampaignFormData } from './types';

type Page = 'home' | 'results';

export default function App() {
  const [page, setPage] = useState<Page>('home');
  const [campaign, setCampaign] = useState<CampaignFormData | null>(null);

  const handleRunCampaign = (data: CampaignFormData) => {
    setCampaign(data);
    setPage('results');
  };

  const handleBack = () => {
    setCampaign(null);
    setPage('home');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar onLogoClick={handleBack} />
      {page === 'home' && <HomePage onSubmit={handleRunCampaign} />}
      {page === 'results' && campaign && (
        <ResultsDashboard campaign={campaign} onBack={handleBack} />
      )}
    </div>
  );
}

export type ScanDepth = 'fast' | 'deep';

export type LeadStatus = 'New' | 'Pending' | 'Sent';

export type StepStatus = 'idle' | 'active' | 'complete';

export interface Lead {
  id: string;
  company: string;
  source: string;
  status: LeadStatus;
  email?: string;
}

export interface GeneratedEmail {
  id: string;
  company: string;
  subject: string;
  body: string;
}

export interface PipelineStep {
  id: number;
  label: string;
  status: StepStatus;
}

export interface CampaignFormData {
  companyName: string;
  websiteUrl: string;
  scanDepth: ScanDepth;
  leads?: any[];
  results?: any[];
  services?: string;
  portfolio?: string;
}

export interface CampaignMetrics {
  leadsFound: number;
  emailsGenerated: number;
  portfolio: number;
  sheetRows: number;
}

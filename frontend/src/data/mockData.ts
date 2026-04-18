import { Lead, GeneratedEmail, CampaignMetrics } from '../types';

export const MOCK_LEADS: Lead[] = [
  { id: '1', company: 'TechCorp Inc.', source: 'LinkedIn', status: 'New', email: 'hello@techcorp.io' },
  { id: '2', company: 'DataFlow Systems', source: 'Website', status: 'Pending', email: 'info@dataflow.com' },
  { id: '3', company: 'CloudBase Ltd.', source: 'LinkedIn', status: 'Sent', email: 'contact@cloudbase.io' },
  { id: '4', company: 'Nexus Analytics', source: 'Directory', status: 'New', email: 'sales@nexusanalytics.com' },
  { id: '5', company: 'Vertex Solutions', source: 'LinkedIn', status: 'Pending', email: 'hello@vertexsol.com' },
  { id: '6', company: 'Apex Digital', source: 'Website', status: 'Sent', email: 'info@apexdigital.co' },
  { id: '7', company: 'Orbit Software', source: 'Directory', status: 'New', email: 'contact@orbitsw.com' },
];

export const MOCK_EMAILS: GeneratedEmail[] = [
  {
    id: '1',
    company: 'TechCorp Inc.',
    subject: 'Streamline Your Marketing Operations with AI',
    body: `Hi TechCorp team,

I came across your platform and was impressed by the scale of your operations. At Smart Marketing Assistant, we help B2B companies like yours automate lead discovery and outreach at scale — reducing manual effort by up to 70%.

Here's what we can do for TechCorp:
• Identify high-intent leads across LinkedIn, directories, and the web
• Auto-generate personalized email sequences in seconds
• Track campaign performance in a unified dashboard

I'd love to schedule a 20-minute demo at your convenience. Would next Tuesday or Wednesday work?

Looking forward to connecting.

Best regards,
The Smart Marketing Assistant Team`,
  },
  {
    id: '2',
    company: 'DataFlow Systems',
    subject: 'Automate Your B2B Lead Generation — Built for DataFlow',
    body: `Hello DataFlow team,

Your work in data pipeline orchestration is impressive — I can see why your customer base has grown so rapidly. That's exactly the kind of growth we help sustain at scale.

Smart Marketing Assistant gives data-driven companies like DataFlow a powerful edge:
• AI-powered prospect research tailored to your ICP
• Automated, personalized email drafting from a single click
• Google Sheets & Drive integration for seamless handoffs

Can we hop on a quick call this week to explore how this fits your outbound motion?

Cheers,
Smart Marketing Assistant Team`,
  },
  {
    id: '3',
    company: 'Nexus Analytics',
    subject: 'Turning Insights Into Pipeline — For Nexus Analytics',
    body: `Hi Nexus Analytics,

Analytics teams have more data than ever, yet outbound sales still relies on manual prospecting. That gap is exactly what Smart Marketing Assistant was built to close.

We help analytics-first companies:
• Discover decision-makers from multiple data sources automatically
• Generate context-aware outreach in your brand voice
• Push campaign results directly into your existing workflows

Would a 15-minute overview this week be of interest? I can walk you through a live demo tailored to your stack.

Best,
Smart Marketing Assistant Team`,
  },
];

export const MOCK_METRICS: CampaignMetrics = {
  leadsFound: 24,
  emailsGenerated: 18,
  portfolio: 1,
  sheetRows: 24,
};

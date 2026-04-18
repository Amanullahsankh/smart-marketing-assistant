/*
  # Smart Marketing Assistant – Initial Schema

  ## Overview
  Creates the core tables for the Smart Marketing Assistant B2B SaaS dashboard.

  ## New Tables

  ### campaigns
  Stores each marketing campaign run by a user.
  - id (uuid, primary key)
  - company_name (text) – the target company name entered on the home page
  - website_url (text) – the URL scanned
  - scan_depth (text) – "fast" or "deep"
  - status (text) – "running" | "complete" | "failed"
  - created_at (timestamptz)

  ### leads
  Stores discovered leads associated with a campaign.
  - id (uuid, primary key)
  - campaign_id (uuid, FK → campaigns.id)
  - company (text) – lead company name
  - source (text) – where the lead was found (LinkedIn, Website, Directory)
  - status (text) – "New" | "Pending" | "Sent"
  - email (text, nullable)
  - created_at (timestamptz)

  ### generated_emails
  Stores AI-generated outreach emails for each lead.
  - id (uuid, primary key)
  - campaign_id (uuid, FK → campaigns.id)
  - lead_id (uuid, nullable FK → leads.id)
  - company (text)
  - subject (text)
  - body (text)
  - created_at (timestamptz)

  ## Security
  - RLS enabled on all tables
  - Authenticated users can only read/write their own data via user_id column
*/

CREATE TABLE IF NOT EXISTS campaigns (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
  company_name text NOT NULL DEFAULT '',
  website_url text NOT NULL DEFAULT '',
  scan_depth text NOT NULL DEFAULT 'fast',
  status text NOT NULL DEFAULT 'running',
  created_at timestamptz DEFAULT now()
);

ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can select own campaigns"
  ON campaigns FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own campaigns"
  ON campaigns FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own campaigns"
  ON campaigns FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE TABLE IF NOT EXISTS leads (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id uuid REFERENCES campaigns(id) ON DELETE CASCADE NOT NULL,
  company text NOT NULL DEFAULT '',
  source text NOT NULL DEFAULT '',
  status text NOT NULL DEFAULT 'New',
  email text,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE leads ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can select leads for own campaigns"
  ON leads FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM campaigns
      WHERE campaigns.id = leads.campaign_id
      AND campaigns.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert leads for own campaigns"
  ON leads FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM campaigns
      WHERE campaigns.id = leads.campaign_id
      AND campaigns.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update leads for own campaigns"
  ON leads FOR UPDATE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM campaigns
      WHERE campaigns.id = leads.campaign_id
      AND campaigns.user_id = auth.uid()
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM campaigns
      WHERE campaigns.id = leads.campaign_id
      AND campaigns.user_id = auth.uid()
    )
  );

CREATE TABLE IF NOT EXISTS generated_emails (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id uuid REFERENCES campaigns(id) ON DELETE CASCADE NOT NULL,
  lead_id uuid REFERENCES leads(id) ON DELETE SET NULL,
  company text NOT NULL DEFAULT '',
  subject text NOT NULL DEFAULT '',
  body text NOT NULL DEFAULT '',
  created_at timestamptz DEFAULT now()
);

ALTER TABLE generated_emails ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can select emails for own campaigns"
  ON generated_emails FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM campaigns
      WHERE campaigns.id = generated_emails.campaign_id
      AND campaigns.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert emails for own campaigns"
  ON generated_emails FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM campaigns
      WHERE campaigns.id = generated_emails.campaign_id
      AND campaigns.user_id = auth.uid()
    )
  );

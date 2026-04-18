import streamlit as st
import os
import time

st.set_page_config(
    page_title="Smart Marketing Assistant",
    page_icon="assets/favicon.ico",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Inject professional CSS ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Top navbar */
.navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 2rem;
    border-bottom: 1px solid #e5e7eb;
    background: #ffffff;
    margin: -2rem -2rem 2rem -2rem;
}
.nav-logo { font-size: 18px; font-weight: 600; color: #0f172a; }
.nav-badge {
    font-size: 11px;
    padding: 4px 12px;
    background: #eff6ff;
    color: #1d4ed8;
    border-radius: 99px;
    font-weight: 500;
}

/* Section labels */
.section-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.07em;
    color: #9ca3af;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    margin-top: 1.5rem;
}

/* Metric cards */
.metric-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin: 1rem 0;
}
.metric-card {
    background: #f8fafc;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    border: 1px solid #f1f5f9;
}
.metric-label { font-size: 12px; color: #64748b; margin-bottom: 4px; }
.metric-value { font-size: 26px; font-weight: 600; color: #0f172a; }
.metric-sub { font-size: 11px; color: #94a3b8; margin-top: 2px; }

/* Pipeline steps */
.pipeline {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 1rem 0;
    overflow-x: auto;
}
.step-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 10px 16px;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    background: #f8fafc;
    min-width: 100px;
    font-size: 11px;
    color: #94a3b8;
    text-align: center;
    gap: 4px;
}
.step-done { background: #f0fdf4; border-color: #86efac; color: #16a34a; }
.step-active { background: #eff6ff; border-color: #93c5fd; color: #1d4ed8; font-weight: 500; }
.step-arrow { color: #cbd5e1; font-size: 16px; padding: 0 2px; }

/* Lead table */
.lead-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}
.lead-table th {
    text-align: left;
    font-size: 11px;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 0 1rem 10px 0;
    border-bottom: 1px solid #f1f5f9;
}
.lead-table td {
    padding: 10px 1rem 10px 0;
    border-bottom: 1px solid #f8fafc;
    color: #0f172a;
    vertical-align: middle;
}

/* Status pills */
.pill {
    display: inline-block;
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 99px;
    font-weight: 500;
}
.pill-new { background: #eff6ff; color: #1d4ed8; }
.pill-pending { background: #fffbeb; color: #b45309; }
.pill-sent { background: #f0fdf4; color: #16a34a; }

/* Override Streamlit button */
.stButton > button {
    background: #1d4ed8 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 0.6rem 2rem !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #1e40af !important;
}

/* Input fields */
.stTextInput > div > div > input {
    border-radius: 8px !important;
    border: 1px solid #e2e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    padding: 0.5rem 0.75rem !important;
}

/* Expander (email cards) */
.streamlit-expanderHeader {
    background: #f8fafc !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Safe imports ────────────────────────────────────────────────────
try:
    from extractor import extract_services, is_valid_service_text
except ImportError:
    extract_services = lambda url, limit=3: "Could not extract services."
    is_valid_service_text = lambda t: False

try:
    from discovery import discover_clients
except ImportError:
    discover_clients = lambda s: []

try:
    from summarizer import summarize_client
except ImportError:
    summarize_client = lambda c: "No summary available."

try:
    from emailer import generate_email
except ImportError:
    generate_email = lambda *a, **k: {"subject": "Demo Subject", "body": "Demo email body."}

try:
    from portfolio import create_portfolio
except ImportError:
    create_portfolio = lambda n, t: f"{n}_Portfolio.pdf"

try:
    from drive_uploader import upload_to_drive
except ImportError:
    upload_to_drive = lambda f: None

try:
    from sheets_logger import log_to_sheet
except ImportError:
    log_to_sheet = lambda r: None


# ── Navbar ──────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
    <span class="nav-logo">Smart Marketing Assistant</span>
    <span class="nav-badge">AI-Powered</span>
</div>
""", unsafe_allow_html=True)


# ── Layout: two columns ─────────────────────────────────────────────
left_col, right_col = st.columns([1, 2], gap="large")

with left_col:
    st.markdown('<div class="section-label">Campaign Setup</div>', unsafe_allow_html=True)

    business_name = st.text_input("Company name", placeholder="e.g. NextGen Solutions")
    website_url   = st.text_input("Website URL", placeholder="https://www.yourcompany.com")

    st.markdown('<div class="section-label" style="margin-top:1rem;">Scan depth</div>', unsafe_allow_html=True)
    speed_mode = st.radio(
        "",
        ["Fast scan — 2 pages (~30s)", "Deep scan — 5 pages (more leads)"],
        index=0,
        label_visibility="collapsed"
    )
    page_limit = 2 if "Fast" in speed_mode else 5

    run = st.button("Run marketing assistant")


# ── Right column: results ───────────────────────────────────────────
with right_col:
    if run:
        if not business_name or not website_url:
            st.error("Please enter both company name and website URL.")
            st.stop()

        # Pipeline tracker
        def render_pipeline(active_step):
            steps = ["Extract services", "Discover leads",
                     "Summarize clients", "Generate emails",
                     "Build portfolio", "Upload & log"]
            boxes = ""
            for i, s in enumerate(steps):
                cls = "step-done" if i < active_step else ("step-active" if i == active_step else "step-box")
                boxes += f'<div class="step-box {cls}"><span style="font-size:10px;opacity:0.7;">0{i+1}</span>{s}</div>'
                if i < len(steps) - 1:
                    boxes += '<span class="step-arrow">›</span>'
            st.markdown(f'<div class="pipeline">{boxes}</div>', unsafe_allow_html=True)

        # ── Step 1
        render_pipeline(0)
        with st.spinner("Extracting services from website..."):
            try:
                services_text = extract_services(website_url, limit=page_limit)
            except Exception as e:
                st.error(f"Extraction failed: {e}")
                st.stop()

            if not services_text or not services_text.strip():
                st.error("Could not extract services. Please check the URL.")
                st.stop()
            if not is_valid_service_text(services_text):
                st.error("Service extraction failed. Try a different URL.")
                st.stop()

        st.markdown('<div class="section-label">Extracted Services</div>', unsafe_allow_html=True)
        tags = "".join([
            f'<span style="display:inline-block;font-size:12px;padding:4px 12px;'
            f'background:#f1f5f9;border-radius:99px;margin:3px;color:#334155;">'
            f'{line.strip("•-* ").split(":")[0]}</span>'
            for line in services_text.splitlines() if line.strip()
        ])
        st.markdown(f'<div style="margin-bottom:1rem;">{tags}</div>', unsafe_allow_html=True)

        # ── Step 2
        render_pipeline(1)
        with st.spinner("Discovering potential client companies..."):
            leads = discover_clients(services_text)
            if not leads:
                st.warning("No leads found. Using demo data.")
                leads = [{"title": "Demo Client", "link": "#"}]

        # ── Steps 3 & 4
        render_pipeline(2)
        results = []
        progress = st.progress(0)
        for i, client in enumerate(leads):
            try:
                summary = summarize_client(client)
                email   = generate_email(business_name, website_url, services_text, client, summary)
                results.append({"client": client, "summary": summary, "email": email})
            except Exception as e:
                st.warning(f"Could not process {client.get('title', 'Unknown')}: {e}")
            progress.progress((i + 1) / len(leads))

        # ── Metrics
        render_pipeline(4)
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card">
                <div class="metric-label">Leads found</div>
                <div class="metric-value">{len(leads)}</div>
                <div class="metric-sub">from website scan</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Emails generated</div>
                <div class="metric-value">{len(results)}</div>
                <div class="metric-sub">ready to send</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Portfolio</div>
                <div class="metric-value">1</div>
                <div class="metric-sub">PDF created</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Sheet rows</div>
                <div class="metric-value">{len(results)}</div>
                <div class="metric-sub">logged to Drive</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Leads table
        st.markdown('<div class="section-label">Potential Leads</div>', unsafe_allow_html=True)
        rows = ""
        for r in results[:10]:
            c = r["client"]
            title = c.get("title", "Unknown")
            link  = c.get("link", "#")
            name_cell = f'<a href="{link}" target="_blank" style="color:#1d4ed8;text-decoration:none;font-weight:500;">{title}</a>' if link != "#" else f'<span style="font-weight:500;">{title}</span>'
            rows += f"""
            <tr>
                <td>{name_cell}</td>
                <td style="color:#94a3b8;">AI discovery</td>
                <td><span class="pill pill-new">New</span></td>
            </tr>"""

        st.markdown(f"""
        <table class="lead-table">
            <thead><tr><th>Company</th><th>Source</th><th>Status</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
        """, unsafe_allow_html=True)

        # ── Emails
        st.markdown('<div class="section-label" style="margin-top:1.5rem;">Generated Emails</div>', unsafe_allow_html=True)
        for r in results:
            client     = r["client"]
            email_data = r.get("email", {})
            subject    = email_data.get("subject", "No subject") if isinstance(email_data, dict) else "No subject"
            body       = email_data.get("body", "No body.")    if isinstance(email_data, dict) else str(email_data)
            with st.expander(f"{client.get('title', 'Unknown')}  —  {subject}"):
                st.markdown(f"**Subject:** {subject}")
                st.markdown("---")
                st.markdown(body)

        # ── Portfolio
        with st.spinner("Building portfolio PDF..."):
            pdf_path = create_portfolio(business_name, services_text)

        # ── Drive upload
        file_id = None
        with st.spinner("Uploading to Google Drive..."):
            try:
                file_id = upload_to_drive(os.path.basename(pdf_path))
            except Exception as e:
                st.warning(f"Drive upload failed: {e}")

        # ── Sheets log
        render_pipeline(5)
        with st.spinner("Logging to Google Sheets..."):
            try:
                for r in results:
                    s = r.get("summary", "")
                    r["summary"]   = s.get("summary", "") if isinstance(s, dict) else str(s)
                    r["portfolio"] = os.path.basename(pdf_path)
                log_to_sheet(results)
            except Exception as e:
                st.warning(f"Sheet logging skipped: {e}")

        # ── Output links
        st.markdown('<div class="section-label" style="margin-top:1.5rem;">Outputs</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if file_id:
                st.markdown(f'<a href="https://drive.google.com/file/d/{file_id}/view" target="_blank" style="display:block;text-align:center;padding:0.6rem;background:#f0fdf4;border:1px solid #86efac;border-radius:8px;color:#16a34a;font-size:13px;font-weight:500;text-decoration:none;">View Portfolio on Drive</a>', unsafe_allow_html=True)
            else:
                st.info("Portfolio upload skipped.")
        with col2:
            sheet_link = "https://docs.google.com/spreadsheets/d/16MvwG0MAbRhDNJVB34Dhcc9l45hO7qRnkBJLXYJufYQ"
            st.markdown(f'<a href="{sheet_link}" target="_blank" style="display:block;text-align:center;padding:0.6rem;background:#eff6ff;border:1px solid #93c5fd;border-radius:8px;color:#1d4ed8;font-size:13px;font-weight:500;text-decoration:none;">Open Google Sheet</a>', unsafe_allow_html=True)

        st.balloons()

    else:
        st.markdown("""
        <div style="padding:3rem 2rem;text-align:center;color:#94a3b8;">
            <div style="font-size:14px;margin-bottom:0.5rem;">Enter your company details and click</div>
            <div style="font-size:16px;font-weight:500;color:#64748b;">Run marketing assistant</div>
            <div style="font-size:13px;margin-top:1rem;line-height:1.8;">
                The pipeline will extract your services, discover leads,<br>
                generate personalized emails and build your portfolio.
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;font-size:11px;color:#94a3b8;margin-top:3rem;padding-top:1rem;border-top:1px solid #f1f5f9;">
    Smart Marketing Assistant &nbsp;·&nbsp; VTU Hackathon 2025 &nbsp;·&nbsp; Built by Amanullah & Team
</div>
""", unsafe_allow_html=True)
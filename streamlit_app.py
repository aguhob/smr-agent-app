import streamlit as st
import openai
import requests
import datetime
from fpdf import FPDF
import smtplib
from email.message import EmailMessage

# Replace with your actual API keys and credentials
os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
AIRTABLE_API_KEY = "patVw0aOUnFYSWJ4N.d6f66d7fc31d437fbb91b33c68d44425ef4d673f0bf0142603512102b01945df"
AIRTABLE_BASE_ID = "appVYKA73Mu0Bv1GT"
AIRTABLE_PROJECTS_TABLE = "Projects"
AIRTABLE_RISKS_TABLE = "Risks"
AIRTABLE_MITIGATIONS_TABLE = "Mitigations"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "you@example.com"
EMAIL_PASSWORD = "yourpassword"
EMAIL_RECIPIENT = "stakeholder@example.com"

st.title("Infrastructure AI Agent Pipeline")
st.write("Submit a project to evaluate viability, risks, and mitigation strategies.")

project_name = st.text_input("Project Name")
location = st.text_input("Location")
infra_type = st.multiselect("Infrastructure Type", ["SMR", "Solar", "Wind", "Data Center", "Transmission", "Hybrid"])
objective = st.text_area("Strategic Objective")
anticipated_risks = st.multiselect("Anticipated Risks", ["CAPEX", "Timeline", "Political", "Regulatory", "Community", "Climate"])
community_signals = st.text_area("Community Signals (optional)")
timeline_constraints = st.text_input("Timeline Constraints")
known_partners = st.text_input("Known Developers or Partners")

if st.button("Run Full Agent Analysis"):
    with st.spinner("Running Agent 1: Strategic Recommendation..."):
        agent1_prompt = f"""
        You are Agent 1, a strategic infrastructure advisor. Evaluate the following:
        Project: {project_name} in {location}
        Type: {', '.join(infra_type)}
        Objective: {objective}
        Known Risks: {', '.join(anticipated_risks)}
        Community Signals: {community_signals}
        Constraints: {timeline_constraints}
        Partners: {known_partners}
        Respond with: 1) Summary of risks, 2) Recommendation, 3) One-sentence rationale, 4) Rationale details.
        """
        agent1 = openai.ChatCompletion.create(model="gpt-4", messages=[
            {"role": "system", "content": "You are a strategic advisor."},
            {"role": "user", "content": agent1_prompt}
        ])
        agent1_output = agent1['choices'][0]['message']['content']

    with st.spinner("Running Agent 2: Risk Identification..."):
        agent2_prompt = f"""
        You are Agent 2, a risk translator. Identify 3–5 core risks in:
        Project: {project_name}, Objective: {objective}, Community: {community_signals}
        Output: Risk Type, Description, Urgency Level.
        """
        agent2 = openai.ChatCompletion.create(model="gpt-4", messages=[
            {"role": "system", "content": "You are a nuclear risk analyst."},
            {"role": "user", "content": agent2_prompt}
        ])
        agent2_output = agent2['choices'][0]['message']['content']

    with st.spinner("Running Agent 3: Mitigation Planning..."):
        agent3_prompt = f"""
        You are Agent 3, a mitigation planner. Given these risks:
        {agent2_output}
        Generate: Mitigation Strategy per risk, plus execution steps.
        """
        agent3 = openai.ChatCompletion.create(model="gpt-4", messages=[
            {"role": "system", "content": "You are a risk mitigation strategist."},
            {"role": "user", "content": agent3_prompt}
        ])
        agent3_output = agent3['choices'][0]['message']['content']

    # Generate PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Project Summary\nDate: {datetime.datetime.now().strftime('%Y-%m-%d')}\nProject: {project_name}\nLocation: {location}\nType: {', '.join(infra_type)}\nObjective: {objective}\nKnown Partners: {known_partners}")
    pdf.ln(5)
    pdf.multi_cell(0, 10, f"Agent 1 Output:\n{agent1_output}")
    pdf.add_page()
    pdf.multi_cell(0, 10, f"Agent 2 Risk Summary:\n{agent2_output}")
    pdf.add_page()
    pdf.multi_cell(0, 10, f"Agent 3 Mitigation Plan:\n{agent3_output}")
    pdf_path = f"{project_name.replace(' ', '_')}_AI_Plan.pdf"
    pdf.output(pdf_path)
    st.success("PDF Generated!")
    st.download_button("Download PDF", file_name=pdf_path.split("/")[-1], data=open(pdf_path, "rb"), mime="application/pdf")

    # Email PDF
    msg = EmailMessage()
    msg["Subject"] = f"AI Project Review: {project_name}"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECIPIENT
    msg.set_content(f"Attached is the full AI analysis for project: {project_name}")
    with open(pdf_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=pdf_path.split("/")[-1])
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
    st.success("PDF emailed to stakeholder!")

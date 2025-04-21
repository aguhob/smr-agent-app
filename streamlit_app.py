import streamlit as st
from openai import OpenAI
import requests
import datetime
from fpdf import FPDF
import smtplib
from email.message import EmailMessage

# Replace with your actual API keys and credentials
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")
AIRTABLE_API_KEY = "YOUR_AIRTABLE_API_KEY"
AIRTABLE_BASE_ID = "YOUR_AIRTABLE_BASE_ID"
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

power_type = st.multiselect("Type of Power Generation Being Considered", [
    "Small Modular Reactor",
    "Large Giga-scale Reactor",
    "Natural Gas Turbine",
    "Wind Farm",
    "Solar Photovoltaic Farm",
    "Hybrid -- Wind/Solar+LDES",
    "Hybrid -- SMR+Natural Gas",
    "Geothermal"
])

infra_type = st.multiselect("Type of Infrastructure Being Considered", [
    "Data Center Power",
    "Industrial Heat and Power",
    "Grid Power",
    "Carbon Capture Storage + Utilization Power",
    "Remote Community Power",
    "Advanced Low-Carbon Fuels + Materials"
])

strategic_objectives = st.multiselect("Strategic Objectives Being Considered", [
    "Enhance Energy Security + Safety Systems",
    "Improve Fuel Utilization + Waste Reduction",
    "Build a Skilled Workforce",
    "Build Public Trust",
    "Reduce Reliance on Fossil Fuels + Support Decarbonization Goals",
    "Reduce Construction + Operating Costs",
    "Streamline + Align Construction Processes"
])

anticipated_risks = st.multiselect("What Risks Do You Anticipate?", [
    "High Construction Costs",
    "Long Project Timelines",
    "Safety Concerns",
    "Competition from Cheaper Energy Sources",
    "Complex + Inadequate Regulatory Framework",
    "Significant Upfront Capital Investment"
])

timeline_constraints = st.multiselect("Desired Timeline or Constraints Being Considered", [
    "Prototypes & Proof of Concept",
    "Memorandums of Understanding",
    "Power Purchase Agreements",
    "Regulator Engagement",
    "Construction & Development",
    "Other…"
])

known_partners = st.text_input("Who are Some Known Developers, Vendors or Partners")

if st.button("Run Full Agent Analysis"):
    with st.spinner("Running Agent 1: Strategic Recommendation..."):
        agent1_prompt = f"""
        You are Agent 1, a strategic infrastructure advisor. Evaluate the following:
        Project: {project_name} in {location}
        Power Type: {', '.join(power_type)}
        Infrastructure Type: {', '.join(infra_type)}
        Objectives: {', '.join(strategic_objectives)}
        Known Risks: {', '.join(anticipated_risks)}
        Constraints: {', '.join(timeline_constraints)}
        Partners: {known_partners}
        Respond with: 1) Summary of risks, 2) Recommendation, 3) One-sentence rationale, 4) Rationale details.
        """
        agent1 = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a strategic advisor."},
                {"role": "user", "content": agent1_prompt}
            ]
        )
        agent1_output = agent1.choices[0].message.content

    with st.spinner("Running Agent 2: Risk Identification..."):
        agent2_prompt = f"""
        You are Agent 2, a risk translator. Identify 3–5 core risks in:
        Project: {project_name}, Objectives: {', '.join(strategic_objectives)}
        Output: Risk Type, Description, Urgency Level.
        """
        agent2 = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a nuclear risk analyst."},
                {"role": "user", "content": agent2_prompt}
            ]
        )
        agent2_output = agent2.choices[0].message.content

    with st.spinner("Running Agent 3: Mitigation Planning..."):
        agent3_prompt = f"""
        You are Agent 3, a mitigation planner. Given these risks:
        {agent2_output}
        Generate: Mitigation Strategy per risk, plus execution steps.
        """
        agent3 = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a risk mitigation strategist."},
                {"role": "user", "content": agent3_prompt}
            ]
        )
        agent3_output = agent3.choices[0].message.content

    # Generate PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Project Summary\nDate: {datetime.datetime.now().strftime('%Y-%m-%d')}\nProject: {project_name}\nLocation: {location}\nPower Type: {', '.join(power_type)}\nInfrastructure Type: {', '.join(infra_type)}\nObjectives: {', '.join(strategic_objectives)}\nPartners: {known_partners}")
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

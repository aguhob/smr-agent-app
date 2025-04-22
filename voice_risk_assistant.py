import streamlit as st
import openai
from streamlit_audiorecorder import audiorecorder
import tempfile
import json

st.set_page_config(page_title="🎙️ Voice Risk Assistant")
st.title("🎙️ Developer Risk Voice Assistant")
st.markdown("Speak your concern and get an AI-generated risk insight, enhanced with local data and community feedback.")

# Load enhanced risk data
try:
    with open("enhanced_risk_data.json", "r") as f:
        enhanced_data = json.load(f)
except FileNotFoundError:
    enhanced_data = {}

# Placeholder: Load agent outputs from prior pipeline (for demo)
agent1_output = "SMRs may face local permitting resistance in flood-prone zones."
agent2_output = "Key risks: Environmental flooding, regulatory delays."
agent3_output = "Mitigation: Engage early with local water boards and initiate pre-permitting assessments."

# Voice input
audio = audiorecorder("Click to record your question", "Recording...")

if audio:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio.tobytes())
        f.flush()
        transcript = openai.Audio.transcribe("whisper-1", f)["text"]
    st.markdown(f"**You said:** {transcript}")

    # Extract location if mentioned in voice (or ask user to specify)
    location = st.text_input("Which city or region are you referring to?", "San Antonio")

    # Merge data for assistant context
    city_context = enhanced_data.get(location, [])
    community_feedback = "Recent concerns include permitting delays and water usage impacts."

    combined_context = f"""
    Strategic Advisory: {agent1_output}
    Risk Summary: {agent2_output}
    Mitigation Plan: {agent3_output}

    Local Intelligence:
    {json.dumps(city_context, indent=2)}

    Community Feedback:
    {community_feedback}
    """

    # GPT response
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful and clear risk mitigation advisor for energy projects."},
            {"role": "user", "content": f"User asked: '{transcript}'\n\nContext:\n{combined_context}"}
        ]
    )

    reply = response["choices"][0]["message"]["content"]
    st.markdown(f"**AI Assistant says:** {reply}")

import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
import base64
import extra_streamlit_components as stx  # Kept for future use, but not needed here
import time
import streamlit.components.v1 as components  # For html rendering

# Load .env
load_dotenv()

# === CONFIG ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("Please set GEMINI_API_KEY in your .env file")
    st.stop()

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="Gemini IR Playbook Generator", layout="wide")
st.title("Automated Incident Response Playbook Generator")
st.markdown("##### Powered by **Google Gemini** • MITRE ATT&CK • Adaptive Playbooks")

# Sidebar
with st.sidebar:
    st.header("Incident Input")
    incident_summary = st.text_area(
        "Incident Summary",
        placeholder="e.g., Ransomware encryption detected across 200+ endpoints, Cobalt Strike beacons observed",
        height=120
    )

    additional_context = st.text_area(
        "Additional Context (Optional)",
        placeholder="• Environment: Windows + Active Directory\n• Tools: Splunk, SentinelOne\n• Known TTPs: T1078, T1003.001",
        height=120
    )

    sophistication = st.selectbox(
        "Attacker Sophistication",
        ["Low", "Medium", "High", "Nation-State"],
        index=2
    )

    selected_model = st.selectbox(
        "Gemini Model",
        ["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"],
        index=0
    )

    st.markdown("---")
    generate = st.button("Generate Playbook", type="primary", use_container_width=True)

# Main layout
col_main, col_flow = st.columns([2.2, 1.3])

if generate and incident_summary.strip():
    with st.spinner("Gemini is building your incident response playbook..."):
        system_prompt = """You are a senior incident response commander and MITRE ATT&CK expert.
Generate highly actionable, enterprise-grade playbooks with clear phases, decision trees, and containment options.
Always include a Mermaid flowchart (flowchart TD syntax) at the end.
Use professional, concise language. Prioritize speed in ransomware and credential theft scenarios."""

        user_prompt = f"""Incident: {incident_summary}
Context: {additional_context or "Not provided"}
Attacker Level: {sophistication}

Generate a full playbook with:
1. Executive Summary
2. Initial Triage & Detection
3. Containment (Immediate + Full)
4. Eradication
5. Recovery & Hardening
6. Decision Branches
7. MITRE ATT&CK Mapping Table
8. Mermaid Flowchart (flowchart TD style)

Output in clean Markdown."""

        # Combine system and user prompts for Gemini (Gemini uses a single prompt with system instruction)
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        # Retry logic
        for attempt in range(3):
            try:
                # Initialize the model
                model = genai.GenerativeModel(
                    model_name=selected_model,
                    generation_config={
                        "temperature": 0.3,
                        "max_output_tokens": 8192,
                    }
                )
                
                # Generate content
                response = model.generate_content(full_prompt)
                full_response = response.text

                # Store
                st.session_state.playbook_md = full_response

                # Extract Mermaid (case-insensitive search)
                mermaid_code = ""
                lower_response = full_response.lower()
                if "```mermaid" in lower_response:
                    start = lower_response.find("```mermaid") + 10
                    end = full_response.find("```", full_response.lower().find("```mermaid") + 10)
                    if end != -1:
                        mermaid_code = full_response[start:end].strip()

                clean_md = full_response.split("```mermaid")[0] if mermaid_code else full_response

                # Display
                with col_main:
                    st.markdown(clean_md, unsafe_allow_html=True)

                with col_flow:
                    st.subheader("Playbook Flowchart")
                    if mermaid_code:
                        # Use native Streamlit components.html for Mermaid
                        html_content = f"""
                        <div class="mermaid">{mermaid_code}</div>
                        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                        <script>
                            mermaid.initialize({{
                                startOnLoad: true,
                                theme: 'base',
                                themeVariables: {{ primaryColor: '#1d4ed8', secondaryColor: '#dc2626' }},
                                flowchart: {{ useMaxWidth: true }}
                            }});
                        </script>
                        """
                        components.html(html_content, height=700, scrolling=True)
                    else:
                        st.info("No flowchart in response")

                break  # Success

            except Exception as e:
                if attempt == 2:
                    error_msg = str(e)
                    if "API_KEY_INVALID" in error_msg or "401" in error_msg:
                        st.error(
                            "### API Key Error\n"
                            "Your Gemini API key is invalid or expired.\n\n"
                            "**How to fix:**\n"
                            "1. Go to https://aistudio.google.com/app/apikey\n"
                            "2. Create a new API key or regenerate an existing one\n"
                            "3. Update your .env file with: `GEMINI_API_KEY=your_key_here`\n"
                        )
                    elif "404" in error_msg or "MODEL_NOT_FOUND" in error_msg:
                        st.error(
                            "### Model Not Found\n"
                            f"The model '{selected_model}' is not available.\n\n"
                            "**Available models:**\n"
                            "- gemini-2.0-flash-exp\n"
                            "- gemini-1.5-pro\n"
                            "- gemini-1.5-flash\n"
                        )
                    else:
                        st.error(f"Failed after 3 attempts: {e}")
                    st.stop()
                else:
                    st.warning(f"Attempt {attempt+1} failed, retrying...")
                    time.sleep(2)

# Export & Refine
if "playbook_md" in st.session_state:
    st.markdown("---")
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        st.download_button("Download Markdown", st.session_state.playbook_md, "IR_Playbook.md", "text/markdown")
    with c2:
        b64 = base64.b64encode(st.session_state.playbook_md.encode()).decode()
        st.markdown(f'<a href="data:text/markdown;base64,{b64}" download="IR_Playbook.md">Download .md (alt)</a>', unsafe_allow_html=True)
    with c3:
        if st.button("Refine Playbook", use_container_width=True):
            st.session_state.refine_mode = True

# Refinement chat
if st.session_state.get("refine_mode"):
    st.markdown("### Refine Playbook")
    if prompt := st.chat_input("e.g., Add SOAR steps, Focus on cloud, Make shorter"):
        with st.spinner("Updating..."):
            try:
                refine_prompt = f"""Refine the existing IR playbook. Return the full updated version.

Original Playbook:
{st.session_state.playbook_md}

Refinement Request: {prompt}"""

                model = genai.GenerativeModel(
                    model_name=selected_model,
                    generation_config={
                        "temperature": 0.2,
                        "max_output_tokens": 8192,
                    }
                )
                
                response = model.generate_content(refine_prompt)
                st.session_state.playbook_md = response.text
                st.rerun()
            except Exception as e:
                st.error(f"Error refining playbook: {e}")

# Footer
st.caption("Built with Google Gemini + Streamlit • For blue teams, by blue teams")
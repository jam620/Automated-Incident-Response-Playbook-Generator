import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
import base64
import extra_streamlit_components as stx  # Kept for future use, but not needed here
import time
import re
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
        ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"],
        index=0,
        help="gemini-1.5-flash is recommended for free tier. gemini-2.0-flash-exp may require paid plan."
    )

    st.markdown("---")
    
    # Quota information
    with st.expander("ℹ️ About API Quotas & Rate Limits"):
        st.markdown("""
        **Free Tier Limits:**
        - `gemini-1.5-flash`: Best for free tier (15 requests/min, 1M tokens/min)
        - `gemini-1.5-pro`: Limited free tier support
        - `gemini-2.0-flash-exp`: May require paid plan
        
        **If you see quota errors:**
        - Switch to `gemini-1.5-flash` (recommended for free tier)
        - Check your usage: https://ai.dev/usage?tab=rate-limit
        - Wait for rate limit reset (usually 1 minute)
        - Consider upgrading: https://ai.google.dev/pricing
        
        The app will automatically retry with exponential backoff on rate limit errors.
        """)
    
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

        # Retry logic with exponential backoff for rate limits
        max_attempts = 5
        for attempt in range(max_attempts):
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
                error_msg = str(e)
                
                # Handle rate limit errors (429) with exponential backoff
                if "429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                    if attempt < max_attempts - 1:
                        # Extract retry delay from error if available, otherwise use exponential backoff
                        retry_delay = min(2 ** attempt * 2, 60)  # Exponential backoff: 2s, 4s, 8s, 16s, max 60s
                        
                        # Try to extract retry_delay from error message
                        if "retry_delay" in error_msg or "retry in" in error_msg.lower():
                            delay_match = re.search(r'retry.*?(\d+\.?\d*)\s*s', error_msg, re.IGNORECASE)
                            if delay_match:
                                retry_delay = float(delay_match.group(1)) + 2  # Add 2s buffer
                        
                        st.warning(
                            f"⚠️ **Rate Limit Exceeded** (Attempt {attempt+1}/{max_attempts})\n\n"
                            f"Waiting {int(retry_delay)} seconds before retry...\n\n"
                            "**Tips:**\n"
                            "- Switch to `gemini-1.5-flash` for better free tier support\n"
                            "- Check your quota: https://ai.dev/usage?tab=rate-limit\n"
                            "- Consider upgrading if you need higher limits"
                        )
                        time.sleep(retry_delay)
                        continue
                    else:
                        st.error(
                            "### Rate Limit Exceeded\n\n"
                            "**Maximum retries reached. The API quota has been exceeded.**\n\n"
                            "**Solutions:**\n"
                            "1. **Switch to `gemini-1.5-flash`** (best for free tier)\n"
                            "2. **Wait a few minutes** for rate limits to reset\n"
                            "3. **Check your usage:** https://ai.dev/usage?tab=rate-limit\n"
                            "4. **Upgrade your plan:** https://ai.google.dev/pricing\n\n"
                            f"**Error details:** {error_msg[:200]}"
                        )
                        st.stop()
                
                # Handle other errors
                elif attempt == max_attempts - 1:
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
                            "- gemini-1.5-flash (recommended)\n"
                            "- gemini-1.5-pro\n"
                            "- gemini-2.0-flash-exp\n"
                        )
                    else:
                        st.error(f"Failed after {max_attempts} attempts: {e}")
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
            max_refine_attempts = 3
            for refine_attempt in range(max_refine_attempts):
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
                    error_msg = str(e)
                    if ("429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower()) and refine_attempt < max_refine_attempts - 1:
                        retry_delay = min(2 ** refine_attempt * 2, 60)
                        st.warning(f"Rate limit hit. Retrying in {int(retry_delay)} seconds...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        st.error(f"Error refining playbook: {e}")
                        break

# Footer
st.caption("Built with Google Gemini + Streamlit • For blue teams, by blue teams")
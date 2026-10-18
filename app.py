"""
AI Agent for Smart Farming Advice
Main Streamlit Application
IBM Granite + IBM Cloud powered multi-agent farming assistant
"""
import streamlit as st
import sys
import os
import json
from datetime import datetime
from PIL import Image
import io

# ── Path setup ─────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🌾 Smart Farming AI Agent",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .main { background-color: #f5f7f2; }
    
    /* Header */
    .app-header {
        background: linear-gradient(135deg, #1a6b2e 0%, #2d9642 50%, #4caf50 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(45, 150, 66, 0.3);
    }
    .app-header h1 { margin: 0; font-size: 2rem; font-weight: 700; }
    .app-header p { margin: 0.3rem 0 0 0; opacity: 0.9; font-size: 1rem; }
    
    /* Agent cards */
    .agent-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-left: 4px solid #2d9642;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }
    .agent-card h4 { color: #1a6b2e; margin: 0 0 0.5rem 0; font-size: 0.9rem; }
    
    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #e8f5e9;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .metric-card .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a6b2e;
    }
    .metric-card .metric-label {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.2rem;
    }
    
    /* Weather badge */
    .weather-badge {
        background: #e3f2fd;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        border-left: 3px solid #1976d2;
    }
    
    /* Sidebar styling */
    .sidebar-section {
        background: #f0f7f0;
        border-radius: 8px;
        padding: 0.8rem;
        margin-bottom: 1rem;
        border: 1px solid #c8e6c9;
    }
    
    /* Chat messages */
    .chat-user {
        background: #e8f5e9;
        border-radius: 12px 12px 2px 12px;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
        margin-left: 15%;
        border-left: 3px solid #4caf50;
    }
    .chat-assistant {
        background: white;
        border-radius: 12px 12px 12px 2px;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
        margin-right: 10%;
        border-left: 3px solid #1976d2;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }
    .agent-tag {
        font-size: 0.7rem;
        background: #1a6b2e;
        color: white;
        padding: 0.1rem 0.5rem;
        border-radius: 10px;
        margin-bottom: 0.3rem;
        display: inline-block;
    }
    
    /* Success/Warning/Error states */
    .status-ok { color: #2e7d32; font-weight: 600; }
    .status-warn { color: #f57f17; font-weight: 600; }
    .status-err { color: #c62828; font-weight: 600; }
    
    /* Hide Streamlit footer */
    footer { visibility: hidden; }
    
    /* IBM badge */
    .ibm-badge {
        background: #0530ad;
        color: white;
        font-size: 0.7rem;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        display: inline-block;
    }
    
    /* Scrollable chat area */
    .chat-container { max-height: 500px; overflow-y: auto; }
</style>
""", unsafe_allow_html=True)


# ── Session state initialization ───────────────────────────────────────────
def init_session():
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = None
    if "farmer_profile" not in st.session_state:
        st.session_state.farmer_profile = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "dashboard_data" not in st.session_state:
        st.session_state.dashboard_data = None
    if "profile_set" not in st.session_state:
        st.session_state.profile_set = False


@st.cache_resource(show_spinner=False)
def get_orchestrator():
    """Load orchestrator once and cache it."""
    try:
        from agents.orchestrator import SmartFarmingOrchestrator
        return SmartFarmingOrchestrator()
    except Exception as e:
        return None


def format_inr(amount: float) -> str:
    """Format amount as Indian Rupees."""
    if amount >= 10_00_000:
        return f"₹{amount/10_00_000:.2f}L"
    elif amount >= 1000:
        return f"₹{amount/1000:.1f}K"
    return f"₹{amount:.0f}"


# ── Header ─────────────────────────────────────────────────────────────────
def render_header():
    st.markdown("""
    <div class="app-header">
        <h1>🌾 AI Agent for Smart Farming Advice</h1>
        <p>Powered by <span style="font-weight:700;">IBM Granite</span> · Multi-Agent AI System · RAG-Enabled Knowledge Base</p>
    </div>
    """, unsafe_allow_html=True)


# ── Sidebar ─────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("### 👨‍🌾 Farmer Profile")

        with st.form("farmer_form"):
            name = st.text_input("Your Name", value="Rajesh Kumar", placeholder="Enter your name")
            location = st.text_input("Location / City", value="Pune", placeholder="e.g., Pune, Delhi, Lucknow")
            state = st.text_input("State", value="Maharashtra", placeholder="e.g., Maharashtra")

            st.markdown("**Farm Details**")
            land_area = st.number_input("Farm Area (hectares)", min_value=0.1, max_value=1000.0, value=2.0, step=0.5)

            crops_input = st.text_input(
                "Crops (comma-separated)",
                value="Soybean, Cotton",
                placeholder="e.g., Wheat, Rice, Tomato"
            )

            soil_type = st.selectbox(
                "Soil Type",
                ["Loamy", "Black (Vertisol)", "Red Laterite", "Sandy", "Alluvial", "Clay"],
                index=1,
            )

            irrigation = st.checkbox("Irrigation Available", value=True)

            farming_type = st.selectbox(
                "Farming Type",
                ["Conventional", "Organic", "Integrated", "Natural Farming"],
                index=0,
            )

            experience = st.selectbox(
                "Experience Level",
                ["Beginner", "Intermediate", "Expert"],
                index=1,
            )

            budget = st.number_input(
                "Season Budget (₹, optional)",
                min_value=0,
                max_value=10_00_000,
                value=50000,
                step=5000,
            )

            submitted = st.form_submit_button("✅ Save Profile & Start", use_container_width=True, type="primary")

        if submitted:
            crops = [c.strip() for c in crops_input.split(",") if c.strip()]
            try:
                from agents.orchestrator import SmartFarmingOrchestrator, FarmerProfile
                orchestrator = get_orchestrator()
                if orchestrator is None:
                    from agents.orchestrator import SmartFarmingOrchestrator
                    orchestrator = SmartFarmingOrchestrator()
                    # Clear cache and reinitialize
                    st.cache_resource.clear()

                profile = FarmerProfile(
                    name=name,
                    location=location,
                    crops=crops,
                    land_area_ha=land_area,
                    soil_type=soil_type.lower().split("(")[0].strip(),
                    irrigation=irrigation,
                    farming_type=farming_type.lower(),
                    experience=experience.lower(),
                    state=state,
                    budget_inr=budget if budget > 0 else None,
                )
                orchestrator.set_farmer_profile(profile)
                st.session_state.orchestrator = orchestrator
                st.session_state.farmer_profile = profile
                st.session_state.profile_set = True
                st.success(f"✅ Profile saved for {name}!")
            except Exception as e:
                st.error(f"Error: {e}")

        # Agent status panel
        st.markdown("---")
        st.markdown("### 🤖 Active Agents")
        agents = [
            ("🌱", "Crop Advisory", "RAG + Granite"),
            ("🌤️", "Weather & Irrigation", "Live Weather"),
            ("🐛", "Pest Detection", "Vision AI"),
            ("📈", "Market Insights", "Price Oracle"),
        ]
        for icon, name_ag, tech in agents:
            st.markdown(f"""
            <div style="display:flex;align-items:center;padding:0.4rem 0;border-bottom:1px solid #e8f5e9;">
                <span style="font-size:1.2rem;margin-right:0.5rem;">{icon}</span>
                <div>
                    <div style="font-weight:600;font-size:0.85rem;color:#1a6b2e;">{name_ag}</div>
                    <div style="font-size:0.7rem;color:#888;">{tech}</div>
                </div>
                <span style="margin-left:auto;font-size:0.7rem;background:#e8f5e9;color:#2e7d32;padding:2px 6px;border-radius:8px;">● Active</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("""
        <div style="text-align:center;padding-top:0.5rem;">
            <span class="ibm-badge">IBM Granite 3.0</span>
            <span class="ibm-badge" style="margin-left:4px;">IBM Cloud</span>
        </div>
        """, unsafe_allow_html=True)


# ── Dashboard Tab ───────────────────────────────────────────────────────────
def render_dashboard():
    if not st.session_state.profile_set or st.session_state.orchestrator is None:
        st.info("👈 Please set your farmer profile in the sidebar to get started.")
        render_demo_dashboard()
        return

    fp = st.session_state.farmer_profile
    orch = st.session_state.orchestrator

    st.subheader(f"🏡 Farm Dashboard — {fp.name}")

    # Load dashboard data
    with st.spinner("Loading farm intelligence dashboard..."):
        try:
            data = orch.get_comprehensive_dashboard()
        except Exception as e:
            st.error(f"Dashboard error: {e}")
            data = {}

    # ── Weather Widget ───────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)

    weather = data.get("weather", {})
    if weather and "temperature" in weather:
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">🌡️ {weather['temperature']}°C</div>
                <div class="metric-label">Temperature | {weather.get('city', fp.location)}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">💧 {weather['humidity']}%</div>
                <div class="metric-label">Humidity</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">🌬️ {weather['wind_speed']} km/h</div>
                <div class="metric-label">Wind Speed</div>
            </div>""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">🌧️ {weather.get('rainfall_mm', 0)} mm</div>
                <div class="metric-label">Today's Rainfall</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.warning("Weather data unavailable. Check your location settings.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Market & Finance Row ─────────────────────────────────────────────
    col_m1, col_m2 = st.columns(2)

    market = data.get("market", {})
    with col_m1:
        st.markdown("#### 📊 Market Overview")
        crop = fp.crops[0] if fp.crops else "wheat"
        msp = market.get("msp")
        mandi = market.get("mandi_prices")
        costs = market.get("input_costs")

        if msp:
            st.metric("MSP (2024-25)", f"₹{msp['msp']}/quintal", delta="Government guaranteed")
        if mandi:
            avg_p = mandi.get("avg", 0)
            min_p = mandi.get("min", 0)
            max_p = mandi.get("max", 0)
            st.markdown(f"""
            <div class="weather-badge">
                <b>Mandi Price Range ({crop.title()})</b><br>
                Min: ₹{min_p} | Avg: ₹{avg_p} | Max: ₹{max_p} per quintal
            </div>""", unsafe_allow_html=True)
        if costs:
            st.metric(
                f"Est. Input Cost ({fp.land_area_ha} ha)",
                format_inr(costs.get("total", 0)),
                delta="Total this season",
            )

    with col_m2:
        st.markdown("#### 🌱 Soil & Crop Info")
        soil = data.get("soil", {})
        if soil and "type" in soil:
            st.markdown(f"""
            <div class="agent-card">
                <h4>🪴 {soil['type']}</h4>
                <b>pH:</b> {soil.get('ph', 'N/A')} &nbsp;|&nbsp; 
                <b>Organic Matter:</b> {soil.get('organic_matter', 'N/A')}%<br>
                <b>N:</b> {soil.get('nitrogen', 'N/A')} &nbsp;|&nbsp;
                <b>P:</b> {soil.get('phosphorus', 'N/A')} &nbsp;|&nbsp;
                <b>K:</b> {soil.get('potassium', 'N/A')}<br>
                <b>Water Holding:</b> {soil.get('water_holding', 'N/A')}<br>
                <b>Best for:</b> {', '.join(soil.get('suitable_crops', [])[:4])}
            </div>""", unsafe_allow_html=True)
        else:
            st.info("Soil data not loaded.")

        st.markdown(f"**Registered Crops:** {' · '.join(['🌿 ' + c for c in fp.crops])}")
        st.markdown(f"**Farm Area:** {fp.land_area_ha} hectares | **Irrigation:** {'✅ Yes' if fp.irrigation else '❌ No'}")
        st.markdown(f"**Farming Type:** {fp.farming_type.title()} | **Experience:** {fp.experience.title()}")

    # ── Quick Tips ───────────────────────────────────────────────────────
    st.markdown("---")
    col_tips, col_actions = st.columns([3, 1])
    with col_tips:
        st.markdown("#### 💡 Quick Monthly Tips")
        if st.button("🔄 Get Tips for This Month", use_container_width=True):
            with st.spinner("Generating tips with IBM Granite..."):
                try:
                    crop = fp.crops[0] if fp.crops else "wheat"
                    tips = orch.get_quick_tips(crop, datetime.now().month)
                    st.success(tips)
                except Exception as e:
                    st.error(f"Error: {e}")

    with col_actions:
        st.markdown("#### ⚡ Quick Actions")
        if st.button("📋 Full Season Plan", use_container_width=True):
            st.session_state.active_tab = "advisory"
            st.rerun()
        if st.button("🌤️ Weather Report", use_container_width=True):
            st.session_state.active_tab = "weather"
            st.rerun()


def render_demo_dashboard():
    """Show a demo dashboard when no profile is set."""
    st.markdown("#### 📊 Demo: Sample Farm Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Temperature", "28°C", delta="Partly Cloudy")
    with col2:
        st.metric("Humidity", "68%", delta="Moderate")
    with col3:
        st.metric("Wind Speed", "12 km/h")
    with col4:
        st.metric("Rainfall", "2.5 mm")

    st.markdown("""
    <div class="agent-card">
        <h4>🌾 Set up your farmer profile to get personalized recommendations!</h4>
        Use the sidebar on the left to enter your farm details and start receiving 
        AI-powered advice from our multi-agent system powered by <b>IBM Granite</b>.
    </div>""", unsafe_allow_html=True)


# ── Chat Tab ────────────────────────────────────────────────────────────────
def render_chat():
    st.subheader("💬 Chat with AI Farming Advisor")
    st.markdown("Ask any farming question — our multi-agent system will route to the best specialist.")

    # Suggested questions
    st.markdown("**Quick Questions:**")
    qcols = st.columns(4)
    quick_qs = [
        ("🌿", "Best fertilizer dose for soybean?"),
        ("🌤️", "Should I irrigate today?"),
        ("🐛", "How to identify fall armyworm?"),
        ("💰", "When should I sell my crop?"),
    ]
    for i, (icon, q) in enumerate(quick_qs):
        with qcols[i]:
            if st.button(f"{icon} {q}", key=f"qq_{i}", use_container_width=True):
                st.session_state.pending_message = q

    st.markdown("---")

    # Image upload for pest detection
    with st.expander("📸 Upload Crop Image for Disease/Pest Detection", expanded=False):
        uploaded_file = st.file_uploader(
            "Upload a photo of your crop showing symptoms",
            type=["jpg", "jpeg", "png", "webp"],
            key="crop_image_upload",
        )
        if uploaded_file:
            st.session_state.uploaded_image = uploaded_file.read()
            img = Image.open(io.BytesIO(st.session_state.uploaded_image))
            st.image(img, caption="Uploaded crop image", width=300)
            st.success("✅ Image ready for analysis. Type your question below.")

    # Chat history display
    st.markdown("#### Conversation")
    chat_container = st.container()
    with chat_container:
        if not st.session_state.messages:
            st.markdown("""
            <div class="agent-card">
                <h4>🤖 Multi-Agent AI Farming Assistant Ready!</h4>
                Ask me anything about your crops, soil, weather, pests, diseases, 
                market prices, or government schemes. I'll connect you with the right specialist agent.
            </div>""", unsafe_allow_html=True)
        else:
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-user">
                        <b>👨‍🌾 {st.session_state.farmer_profile.name if st.session_state.farmer_profile else 'You'}:</b><br>
                        {msg['content']}
                    </div>""", unsafe_allow_html=True)
                else:
                    agent_name = msg.get("agent", "AI Advisor")
                    st.markdown(f"""
                    <div class="chat-assistant">
                        <span class="agent-tag">🤖 {agent_name}</span><br>
                        {msg['content'].replace(chr(10), '<br>')}
                    </div>""", unsafe_allow_html=True)

    # Input area
    st.markdown("---")
    col_input, col_send = st.columns([5, 1])

    # Handle pending message from quick questions
    default_msg = ""
    if "pending_message" in st.session_state and st.session_state.pending_message:
        default_msg = st.session_state.pending_message
        st.session_state.pending_message = ""

    with col_input:
        user_input = st.text_input(
            "Type your farming question...",
            value=default_msg,
            placeholder="e.g., When should I apply the first irrigation to my wheat crop?",
            key="chat_input",
            label_visibility="collapsed",
        )
    with col_send:
        send_clicked = st.button("Send 📤", type="primary", use_container_width=True)

    if send_clicked and user_input.strip():
        _send_chat_message(user_input.strip())


def _send_chat_message(user_input: str):
    """Process and send a chat message."""
    orch = st.session_state.get("orchestrator")

    if orch is None:
        try:
            from agents.orchestrator import SmartFarmingOrchestrator
            orch = SmartFarmingOrchestrator()
            st.session_state.orchestrator = orch
        except Exception as e:
            st.error(f"Could not initialize agent: {e}")
            return

    # Get image if uploaded
    image_bytes = st.session_state.pop("uploaded_image", None)

    # Add user message to UI
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("🤖 AI agents thinking..."):
        try:
            result = orch.chat(user_input, image_bytes=image_bytes)
            response_text = result.get("response", "I couldn't process that request.")
            agent_name = result.get("agent", "AI Advisor")

            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "agent": agent_name,
                "data": result.get("data", {}),
            })
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Sorry, I encountered an error: {str(e)}. Please check your IBM credentials in config.env.",
                "agent": "System",
            })

    st.rerun()


# ── Pest Detection Tab ──────────────────────────────────────────────────────
def render_pest_detection():
    st.subheader("🔍 Pest & Disease Detection")
    st.markdown("Upload a crop image or describe symptoms to get instant diagnosis and treatment recommendations.")

    tab_img, tab_symptoms = st.tabs(["📸 Image Analysis", "📝 Symptom Description"])

    with tab_img:
        col1, col2 = st.columns([1, 1])
        with col1:
            crop_for_img = st.selectbox(
                "Crop",
                ["Wheat", "Rice", "Maize", "Soybean", "Cotton", "Tomato", "Potato", "Onion", "Other"],
                key="pest_crop_img",
            )
            uploaded = st.file_uploader(
                "Upload crop photo",
                type=["jpg", "jpeg", "png", "webp"],
                key="pest_img_upload",
            )
            extra_symptoms = st.text_area(
                "Describe additional symptoms (optional)",
                placeholder="e.g., Leaves turning yellow, white powder on surface",
                height=80,
                key="extra_symptoms",
            )
            analyze_btn = st.button("🔬 Analyze Image", type="primary", use_container_width=True, key="analyze_img")

        with col2:
            if uploaded:
                img = Image.open(uploaded)
                st.image(img, caption="Uploaded image", use_column_width=True)

            if analyze_btn and uploaded:
                img_bytes = uploaded.read() if uploaded else None
                if not img_bytes:
                    uploaded.seek(0)
                    img_bytes = uploaded.read()

                with st.spinner("🤖 Analyzing with IBM Granite AI..."):
                    try:
                        from agents.pest_disease_agent import PestDiseaseAgent
                        agent = PestDiseaseAgent()
                        result = agent.analyze_image(
                            image_bytes=img_bytes,
                            crop=crop_for_img,
                            additional_symptoms=extra_symptoms,
                        )
                        st.markdown("#### 🩺 Diagnosis Report")
                        st.markdown(result["ai_analysis"])

                        if result.get("symptom_db_matches"):
                            st.markdown("#### 📚 Knowledge Base Matches")
                            for match in result["symptom_db_matches"][:2]:
                                d = match["disease"]
                                with st.expander(f"🔴 {d['name']} (Confidence: {match['score']})"):
                                    st.write(f"**Crops Affected:** {', '.join(d['crops'])}")
                                    st.write(f"**Symptoms:** {d['visual_signs']}")
                                    st.write(f"**Treatment:** {d['treatment']}")
                                    st.write(f"**Severity:** {d['severity']}")
                    except Exception as e:
                        st.error(f"Analysis error: {e}")
            elif analyze_btn and not uploaded:
                st.warning("Please upload an image first.")

    with tab_symptoms:
        col1, col2 = st.columns([1, 1])
        with col1:
            crop_sym = st.selectbox(
                "Crop",
                ["Wheat", "Rice", "Maize", "Soybean", "Cotton", "Tomato", "Potato", "Other"],
                key="pest_crop_sym",
            )
            location_sym = st.text_input("Location", key="pest_location")
            symptoms_text = st.text_area(
                "Describe symptoms in detail",
                placeholder="e.g., Leaves have yellow spots with brown edges, some leaves are curling and drying up from the tips. Noticed small insects under the leaves.",
                height=150,
            )
            season_sym = st.selectbox(
                "Month/Season",
                ["January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"],
                index=datetime.now().month - 1,
            )
            diagnose_btn = st.button("🩺 Diagnose", type="primary", use_container_width=True)

        with col2:
            if diagnose_btn and symptoms_text:
                with st.spinner("Analyzing symptoms with IBM Granite..."):
                    try:
                        from agents.pest_disease_agent import PestDiseaseAgent
                        agent = PestDiseaseAgent()
                        result = agent.analyze_symptoms_text(
                            crop=crop_sym,
                            symptoms=symptoms_text,
                            location=location_sym,
                            season=season_sym,
                        )
                        st.markdown("#### 🩺 Diagnosis")
                        st.markdown(result["ai_diagnosis"])

                        if result.get("kb_matches"):
                            st.markdown("#### 📚 Matched Diseases")
                            for m in result["kb_matches"][:3]:
                                d = m["disease"]
                                st.markdown(f"""
                                <div class="agent-card">
                                    <h4>🔴 {d['name']}</h4>
                                    <b>Severity:</b> {d['severity']}<br>
                                    <b>Treatment:</b> {d['treatment']}
                                </div>""", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Diagnosis error: {e}")
            elif diagnose_btn and not symptoms_text:
                st.warning("Please describe the symptoms.")
            else:
                st.info("📋 After entering symptoms and clicking Diagnose, your AI report will appear here.")

                # Show pest calendar option
                st.markdown("---")
                st.markdown("#### 📅 Get Pest Calendar")
                if st.button("Generate Pest Calendar", use_container_width=True):
                    with st.spinner("Generating..."):
                        try:
                            from agents.pest_disease_agent import PestDiseaseAgent
                            agent = PestDiseaseAgent()
                            calendar = agent.get_pest_calendar(crop_sym, location_sym)
                            st.markdown(calendar)
                        except Exception as e:
                            st.error(f"Error: {e}")


# ── Weather Tab ─────────────────────────────────────────────────────────────
def render_weather():
    st.subheader("🌤️ Weather & Irrigation Intelligence")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("#### Input Parameters")
        w_location = st.text_input(
            "Location",
            value=st.session_state.farmer_profile.location if st.session_state.farmer_profile else "Pune",
            key="w_location",
        )
        w_crop = st.selectbox(
            "Crop",
            ["Wheat", "Rice", "Maize", "Soybean", "Cotton", "Tomato", "Potato"],
            key="w_crop",
        )
        w_stage = st.selectbox(
            "Crop Stage",
            ["Initial/Germination", "Vegetative/Tillering", "Flowering/Reproductive", "Grain Filling/Late"],
            key="w_stage",
        )
        w_soil = st.selectbox(
            "Soil Type",
            ["Loamy", "Black (Clay)", "Sandy", "Red Laterite", "Alluvial"],
            key="w_soil",
        )
        w_area = st.number_input(
            "Field Area (ha)",
            value=st.session_state.farmer_profile.land_area_ha if st.session_state.farmer_profile else 1.0,
            min_value=0.1,
            max_value=1000.0,
            key="w_area",
        )
        get_irr_btn = st.button("💧 Get Irrigation Advice", type="primary", use_container_width=True)
        get_weather_btn = st.button("🌤️ Weather Farm Advisory", use_container_width=True)

    with col2:
        if get_irr_btn:
            with st.spinner("Calculating irrigation requirements..."):
                try:
                    from agents.weather_irrigation_agent import WeatherIrrigationAgent
                    agent = WeatherIrrigationAgent()
                    result = agent.get_irrigation_recommendation(
                        location=w_location,
                        crop=w_crop,
                        crop_stage=w_stage,
                        soil_type=w_soil.lower().split("(")[0].strip(),
                        field_area_ha=w_area,
                    )
                    weather = result["weather"]

                    st.markdown(f"""
                    <div class="weather-badge">
                        <b>📍 {weather['city']} Weather</b><br>
                        🌡️ {weather['temperature']}°C (Feels {weather['feels_like']}°C) &nbsp;|&nbsp;
                        💧 {weather['humidity']}% Humidity &nbsp;|&nbsp;
                        🌬️ {weather['wind_speed']} km/h Wind<br>
                        ☁️ {weather['description']} &nbsp;|&nbsp; 🌧️ {weather['rainfall_mm']} mm Rain
                    </div>""", unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)

                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("ET₀ Today", f"{result['et0_mm_day']} mm/day", "Reference evapotranspiration")
                    with col_b:
                        st.metric("Water Needed", f"{result['water_requirement_mm']} mm", f"= {result['water_volume_liters_per_ha']:,.0f} L/ha")
                    with col_c:
                        total_water = result['water_requirement_mm'] * w_area
                        st.metric("Total Volume", f"{total_water:.1f} mm", f"For {w_area} ha field")

                    st.markdown("#### 🤖 AI Irrigation Advisory")
                    st.markdown(result["ai_recommendation"])
                except Exception as e:
                    st.error(f"Error: {e}")

        elif get_weather_btn:
            with st.spinner("Getting weather farm advisory..."):
                try:
                    from agents.weather_irrigation_agent import WeatherIrrigationAgent
                    agent = WeatherIrrigationAgent()
                    crops = st.session_state.farmer_profile.crops if st.session_state.farmer_profile else [w_crop]
                    advisory = agent.get_weather_farm_advisory(w_location, crops)

                    from agents.weather_irrigation_agent import get_weather
                    weather = get_weather(w_location)
                    st.markdown(f"""
                    <div class="weather-badge">
                        <b>📍 {weather['city']} Weather</b><br>
                        🌡️ {weather['temperature']}°C &nbsp;|&nbsp; 💧 {weather['humidity']}% &nbsp;|&nbsp;
                        {weather['description']} &nbsp;|&nbsp; Rain: {weather['rainfall_mm']} mm
                    </div>""", unsafe_allow_html=True)
                    st.markdown("#### 📋 Farm Advisory")
                    st.markdown(advisory)
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.info("👈 Set parameters and click a button to get weather-based farm advice.")

            # Show ET0 explainer
            st.markdown("""
            <div class="agent-card">
                <h4>💡 What does this module do?</h4>
                <b>Evapotranspiration (ET₀)</b> calculation using weather data to determine crop water need.<br>
                <b>Stage-wise Kc factors</b> give accurate crop water requirements.<br>
                <b>Irrigation scheduling</b> optimized for water saving and yield maximization.
            </div>""", unsafe_allow_html=True)


# ── Market Tab ──────────────────────────────────────────────────────────────
def render_market():
    st.subheader("📈 Market Intelligence & Profit Optimization")

    tab_analysis, tab_compare, tab_schemes = st.tabs([
        "💹 Market Analysis", "⚖️ Crop Comparison", "🏛️ Government Schemes"
    ])

    with tab_analysis:
        col1, col2 = st.columns([1, 2])
        with col1:
            m_crop = st.selectbox(
                "Select Crop",
                ["Wheat", "Rice", "Maize", "Soybean", "Cotton", "Tomato", "Onion",
                 "Potato", "Groundnut", "Mustard"],
                key="m_crop",
            )
            m_location = st.text_input(
                "Location",
                value=st.session_state.farmer_profile.location if st.session_state.farmer_profile else "Pune",
                key="m_location",
            )
            m_area = st.number_input(
                "Farm Area (ha)",
                value=st.session_state.farmer_profile.land_area_ha if st.session_state.farmer_profile else 2.0,
                min_value=0.1,
                key="m_area",
            )
            m_yield = st.number_input(
                "Expected Yield (t/ha)",
                value=2.5,
                min_value=0.1,
                max_value=100.0,
                step=0.5,
                key="m_yield",
            )
            analyze_mkt = st.button("📊 Analyze Market", type="primary", use_container_width=True)

        with col2:
            if analyze_mkt:
                with st.spinner("Fetching market intelligence..."):
                    try:
                        from agents.market_agent import MarketInsightsAgent
                        agent = MarketInsightsAgent()
                        result = agent.get_market_analysis(
                            crop=m_crop,
                            location=m_location,
                            land_area_ha=m_area,
                            expected_yield_t_ha=m_yield,
                        )

                        fin = result.get("financials", {})
                        if fin:
                            st.markdown("#### 💰 Financial Projections")
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                st.metric("Total Yield", f"{fin.get('total_yield_tonnes', 0)} tonnes")
                                st.metric("Input Cost", format_inr(fin.get('total_input_cost_inr', 0)))
                            with c2:
                                st.metric("Revenue @ MSP", format_inr(fin.get('revenue_at_msp_inr', 0)))
                                st.metric("Profit @ MSP", format_inr(fin.get('profit_at_msp_inr', 0)),
                                          delta=f"ROI: {fin.get('roi_at_msp_pct', 0)}%")
                            with c3:
                                st.metric("Revenue @ Avg Mandi", format_inr(fin.get('revenue_at_avg_mandi_inr', 0)))
                                st.metric("Profit @ Avg Mandi", format_inr(fin.get('profit_at_avg_mandi_inr', 0)),
                                          delta=f"ROI: {fin.get('roi_at_avg_mandi_pct', 0)}%")

                        st.markdown("---")
                        st.markdown("#### 🤖 AI Market Analysis")
                        st.markdown(result["ai_analysis"])
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.info("Select a crop and click Analyze Market to get AI-powered market insights.")

    with tab_compare:
        st.markdown("#### Compare Multiple Crops for Profitability")
        crops_to_compare = st.multiselect(
            "Select crops to compare",
            ["Wheat", "Rice", "Maize", "Soybean", "Cotton", "Tomato", "Onion", "Potato", "Groundnut", "Mustard"],
            default=["Soybean", "Cotton", "Maize"],
        )
        compare_location = st.text_input(
            "Location",
            value=st.session_state.farmer_profile.location if st.session_state.farmer_profile else "Maharashtra",
            key="compare_location",
        )
        compare_area = st.number_input("Farm Area (ha)", value=2.0, min_value=0.1, key="compare_area")
        compare_season = st.selectbox("Season", ["Kharif", "Rabi", "Zaid"])

        if st.button("⚖️ Compare Crops", type="primary", use_container_width=True) and len(crops_to_compare) >= 2:
            with st.spinner("Comparing crops..."):
                try:
                    from agents.market_agent import MarketInsightsAgent
                    agent = MarketInsightsAgent()
                    comparison = agent.compare_crops(
                        location=compare_location,
                        land_area_ha=compare_area,
                        available_crops=crops_to_compare,
                        season=compare_season,
                    )
                    st.markdown(comparison)
                except Exception as e:
                    st.error(f"Error: {e}")
        elif len(crops_to_compare) < 2:
            st.info("Select at least 2 crops to compare.")

    with tab_schemes:
        st.markdown("#### Government Schemes & Subsidies")
        sch_crop = st.selectbox(
            "Crop",
            ["Wheat", "Rice", "Maize", "Soybean", "Cotton", "Any"],
            key="sch_crop",
        )
        sch_state = st.text_input(
            "State",
            value=st.session_state.farmer_profile.state if st.session_state.farmer_profile else "Maharashtra",
            key="sch_state",
        )
        sch_area = st.number_input("Farm Area (ha)", value=2.0, min_value=0.1, key="sch_area")

        if st.button("🏛️ Get Scheme Benefits", type="primary", use_container_width=True):
            with st.spinner("Looking up government schemes..."):
                try:
                    from agents.market_agent import MarketInsightsAgent
                    agent = MarketInsightsAgent()
                    schemes = agent.get_scheme_benefits(sch_crop, sch_state, sch_area)
                    st.markdown(schemes)
                except Exception as e:
                    st.error(f"Error: {e}")


# ── Advisory Tab ─────────────────────────────────────────────────────────────
def render_advisory():
    st.subheader("🌱 Personalized Crop Advisory")

    tab_plan, tab_fertilizer, tab_seeds = st.tabs([
        "📋 Full Season Plan", "🌿 Fertilizer Schedule", "🌾 Seed Recommendations"
    ])

    with tab_plan:
        col1, col2 = st.columns([1, 2])
        with col1:
            a_name = st.text_input(
                "Farmer Name",
                value=st.session_state.farmer_profile.name if st.session_state.farmer_profile else "Farmer",
                key="a_name",
            )
            a_crop = st.selectbox(
                "Crop",
                ["Wheat", "Rice", "Maize", "Soybean", "Cotton", "Tomato", "Potato", "Onion"],
                key="a_crop",
            )
            a_location = st.text_input(
                "Location",
                value=st.session_state.farmer_profile.location if st.session_state.farmer_profile else "Pune",
                key="a_location",
            )
            a_area = st.number_input(
                "Area (ha)",
                value=st.session_state.farmer_profile.land_area_ha if st.session_state.farmer_profile else 2.0,
                min_value=0.1,
                key="a_area",
            )
            a_soil = st.selectbox(
                "Soil Type",
                ["Loamy", "Black", "Red", "Sandy", "Alluvial"],
                key="a_soil",
            )
            a_irr = st.checkbox("Irrigation Available", value=True, key="a_irr")
            a_farming = st.selectbox("Farming Type", ["Conventional", "Organic", "Integrated"], key="a_farming")
            a_exp = st.selectbox("Experience", ["Beginner", "Intermediate", "Expert"], index=1, key="a_exp")
            a_budget = st.number_input("Budget (₹)", value=50000, min_value=0, step=5000, key="a_budget")
            gen_plan_btn = st.button("📋 Generate Season Plan", type="primary", use_container_width=True)

        with col2:
            if gen_plan_btn:
                with st.spinner("Creating personalized plan with IBM Granite..."):
                    try:
                        from agents.advisory_agent import PersonalizedAdvisoryAgent
                        agent = PersonalizedAdvisoryAgent()
                        result = agent.generate_full_season_plan(
                            farmer_name=a_name,
                            location=a_location,
                            land_area_ha=a_area,
                            crop=a_crop,
                            soil_type=a_soil.lower(),
                            irrigation_available=a_irr,
                            farming_type=a_farming.lower(),
                            budget_inr=a_budget if a_budget > 0 else None,
                            experience_level=a_exp.lower(),
                        )
                        st.markdown(f"#### 📋 Season Plan for {a_name} — {a_crop}")
                        st.markdown(result["season_plan"])

                        if result.get("recommended_varieties"):
                            st.markdown("#### 🌾 Recommended Varieties")
                            for v in result["recommended_varieties"]:
                                st.markdown(f"- **{v['name']}** ({v['type']}): Yield {v['yield']}, Resistance: {v['resistance']}")
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.info("Configure your farm details and click Generate Season Plan for a personalized crop plan.")

    with tab_fertilizer:
        col1, col2 = st.columns([1, 2])
        with col1:
            f_crop = st.selectbox("Crop", ["Wheat", "Rice", "Maize", "Soybean", "Cotton", "Tomato"], key="f_crop")
            f_area = st.number_input("Area (ha)", value=2.0, min_value=0.1, key="f_area")
            f_soil = st.selectbox("Soil Type", ["Loamy", "Black", "Red", "Sandy", "Alluvial"], key="f_soil")
            f_ph = st.slider("Soil pH", 4.0, 9.0, 7.0, 0.1)
            f_om = st.slider("Organic Matter (%)", 0.1, 5.0, 1.5, 0.1)
            fert_btn = st.button("🌿 Get Fertilizer Schedule", type="primary", use_container_width=True)

        with col2:
            if fert_btn:
                with st.spinner("Generating fertilizer schedule..."):
                    try:
                        from agents.advisory_agent import PersonalizedAdvisoryAgent
                        agent = PersonalizedAdvisoryAgent()
                        schedule = agent.get_fertilizer_schedule(f_crop, f_area, f_soil, f_ph, f_om)
                        st.markdown(f"#### 🌿 Fertilizer Schedule for {f_crop}")
                        st.markdown(schedule)
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.info("Set parameters and click Get Fertilizer Schedule.")

    with tab_seeds:
        col1, col2 = st.columns([1, 2])
        with col1:
            s_crop = st.selectbox(
                "Crop",
                ["Wheat", "Rice", "Maize", "Soybean", "Cotton", "Tomato"],
                key="s_crop",
            )
            s_location = st.text_input("Location", key="s_location",
                                       value=st.session_state.farmer_profile.location if st.session_state.farmer_profile else "")
            s_soil = st.selectbox("Soil Type", ["Loamy", "Black", "Red", "Sandy"], key="s_soil")
            s_priority = st.selectbox(
                "Farmer Priority",
                ["Yield (Highest production)", "Disease Resistance", "Drought Tolerance", "Organic / Open Pollinated"],
                key="s_priority",
            )
            seed_btn = st.button("🌾 Get Seed Recommendations", type="primary", use_container_width=True)

        with col2:
            if seed_btn:
                with st.spinner("Analyzing seed options..."):
                    try:
                        from agents.advisory_agent import PersonalizedAdvisoryAgent, SEED_VARIETIES
                        agent = PersonalizedAdvisoryAgent()
                        result = agent.recommend_seeds(
                            crop=s_crop,
                            location=s_location or "India",
                            soil_type=s_soil,
                            priority=s_priority.split("(")[0].strip().lower(),
                        )
                        st.markdown(f"#### 🌾 Seed Recommendations for {s_crop}")
                        st.markdown(result["ai_recommendation"])

                        # Show DB varieties table
                        varieties = result.get("varieties_db", [])
                        if varieties:
                            st.markdown("#### 📚 Available Varieties Reference")
                            for v in varieties:
                                col_v1, col_v2, col_v3 = st.columns(3)
                                col_v1.markdown(f"**{v['name']}**<br><small>{v['type']}</small>", unsafe_allow_html=True)
                                col_v2.markdown(f"Yield: {v['yield']}")
                                col_v3.markdown(f"Resistance: {v['resistance']}")
                                st.markdown("---")
                    except Exception as e:
                        st.error(f"Error: {e}")


# ── Knowledge Base Tab ───────────────────────────────────────────────────────
def render_knowledge():
    st.subheader("📚 Agricultural Knowledge Base (RAG)")
    st.markdown("Search our curated knowledge base powered by Retrieval-Augmented Generation.")

    col1, col2 = st.columns([2, 1])
    with col1:
        kb_query = st.text_area(
            "Ask a farming question",
            placeholder="e.g., How to manage powdery mildew in wheat? What is the best irrigation schedule for soybean?",
            height=100,
            key="kb_query",
        )
        kb_farmer_ctx = st.text_input(
            "Your context (optional)",
            placeholder="e.g., I'm growing wheat in Punjab on alluvial soil",
            key="kb_ctx",
        )
    with col2:
        st.markdown("**Categories:**")
        for cat in ["🌿 Crop Management", "🪴 Soil Health", "🐛 Pest Management", "💧 Irrigation", "💰 Market", "🏛️ Government Schemes"]:
            st.markdown(f"• {cat}")

    if st.button("🔍 Search Knowledge Base", type="primary"):
        if kb_query.strip():
            with st.spinner("Retrieving and generating answer..."):
                try:
                    sys.path.insert(0, os.path.join(BASE_DIR, "data", "knowledge_base"))
                    from rag_agent import AgriculturalRAGAgent
                    agent = AgriculturalRAGAgent()
                    result = agent.query(kb_query, farmer_context=kb_farmer_ctx or None, top_k=3)

                    st.markdown("#### 🤖 AI Answer")
                    st.markdown(result["answer"])

                    if result.get("sources"):
                        st.markdown("#### 📖 Sources")
                        for src in result["sources"]:
                            st.markdown(f"• *{src}*")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a question.")

    # Browse knowledge base
    st.markdown("---")
    st.markdown("#### 📖 Browse Knowledge Base")

    try:
        sys.path.insert(0, os.path.join(BASE_DIR, "data", "knowledge_base"))
        from agricultural_knowledge import get_all_documents, get_documents_by_category
        docs = get_all_documents()

        categories = list(set(d["category"] for d in docs))
        selected_cat = st.selectbox("Filter by Category", ["All"] + categories)

        if selected_cat != "All":
            filtered = get_documents_by_category(selected_cat)
        else:
            filtered = docs

        for doc in filtered[:10]:
            with st.expander(f"📄 {doc['title']}"):
                st.write(doc["content"])
                st.caption(f"Category: {doc['category']} | ID: {doc['id']}")
    except Exception as e:
        st.warning(f"Could not load knowledge base browser: {e}")


# ── Main App ─────────────────────────────────────────────────────────────────
def main():
    init_session()
    render_header()
    render_sidebar()

    # Main navigation tabs
    tabs = st.tabs([
        "🏡 Dashboard",
        "💬 AI Chat",
        "🐛 Pest Detection",
        "🌤️ Weather & Irrigation",
        "📈 Market Intelligence",
        "🌱 Crop Advisory",
        "📚 Knowledge Base",
    ])

    with tabs[0]:
        render_dashboard()
    with tabs[1]:
        render_chat()
    with tabs[2]:
        render_pest_detection()
    with tabs[3]:
        render_weather()
    with tabs[4]:
        render_market()
    with tabs[5]:
        render_advisory()
    with tabs[6]:
        render_knowledge()

    # Footer
    st.markdown("""
    <hr style="margin-top:3rem;">
    <div style="text-align:center;padding:1rem;color:#888;font-size:0.8rem;">
        🌾 AI Agent for Smart Farming Advice &nbsp;|&nbsp; 
        Powered by <b>IBM Granite</b> · <b>IBM watsonx.ai</b> · <b>IBM Cloud</b><br>
        Project ID: 81bcc076-b2a6-4039-a511-842212629b94 &nbsp;|&nbsp; 
        Multi-Agent Architecture: Crop Advisory · Weather & Irrigation · Pest Detection · Market Insights
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Quick test script for the AI Agent for Smart Farming Advice.
Tests each agent and the orchestrator without needing a UI.
Run: python test_agents.py
"""
import sys
import os

# Force UTF-8 output so Indian Rupee symbol etc. display correctly on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "knowledge_base"))

print("=" * 60)
print("  AI Agent for Smart Farming Advice — System Test")
print("=" * 60)

# 1. Test Config
print("\n[1] Testing configuration...")
try:
    import config
    print(f"    [OK] IBM Project ID: {config.IBM_PROJECT_ID[:8]}...")
    print(f"    [OK] IBM Model: {config.GRANITE_CHAT_MODEL}")
    print(f"    [OK] WatsonX URL: {config.IBM_WATSONX_URL}")
except Exception as e:
    print(f"    [FAIL] Config error: {e}")

# 2. Test Knowledge Base
print("\n[2] Testing Knowledge Base & RAG...")
try:
    from data.knowledge_base.agricultural_knowledge import get_all_documents, get_documents_by_category
    docs = get_all_documents()
    print(f"    [OK] Loaded {len(docs)} knowledge base documents")
    crops = get_documents_by_category("crop_management")
    print(f"    [OK] Crop management docs: {len(crops)}")
except Exception as e:
    print(f"    [FAIL] Knowledge Base error: {e}")

# 3. Test RAG Agent (without LLM call)
print("\n[3] Testing RAG Retriever...")
try:
    from data.knowledge_base.rag_agent import SimpleTFIDFRetriever, AgriculturalRAGAgent
    retriever = SimpleTFIDFRetriever()
    from data.knowledge_base.agricultural_knowledge import get_all_documents
    retriever.add_documents(get_all_documents())
    results = retriever.retrieve("wheat fertilizer NPK", top_k=3)
    print(f"    [OK] Retriever working: {len(results)} results for 'wheat fertilizer NPK'")
    for r in results:
        print(f"       - {r['document']['title']} (score: {r['score']:.3f})")
except Exception as e:
    print(f"    [FAIL] RAG Retriever error: {e}")

# 4. Test Weather Agent (demo mode)
print("\n[4] Testing Weather & Irrigation Agent (demo)...")
try:
    from agents.weather_irrigation_agent import get_weather, get_soil_profile
    weather = get_weather("Pune")
    print(f"    [OK] Weather for Pune: {weather['temperature']}°C, {weather['humidity']}% humidity, {weather['description']}")
    soil = get_soil_profile("black")
    print(f"    [OK] Soil profile: {soil['type']}, pH {soil['ph']}")
except Exception as e:
    print(f"    [FAIL] Weather Agent error: {e}")

# 5. Test Market Agent (data only)
print("\n[5] Testing Market Agent (data layer)...")
try:
    from agents.market_agent import get_msp, get_mandi_prices, get_input_costs
    msp = get_msp("wheat")
    print(f"    [OK] Wheat MSP: ₹{msp['msp']}/quintal ({msp['season']})")
    mandi = get_mandi_prices("soybean")
    print(f"    [OK] Soybean mandi range: ₹{mandi['min']}-{mandi['max']}/quintal")
    costs = get_input_costs("cotton", 2.0)
    print(f"    [OK] Cotton input cost (2 ha): ₹{costs['total']:,.0f}")
except Exception as e:
    print(f"    [FAIL] Market Agent error: {e}")

# 6. Test Pest Agent (knowledge base only)
print("\n[6] Testing Pest Detection Agent (KB)...")
try:
    from agents.pest_disease_agent import detect_from_symptoms, DISEASE_SYMPTOMS
    print(f"    [OK] Disease DB loaded: {len(DISEASE_SYMPTOMS)} entries")
    matches = detect_from_symptoms("tomato", "brown spots concentric rings yellow leaves")
    print(f"    [OK] Symptom matching: {len(matches)} matches for tomato brown spots")
    if matches:
        print(f"       Top match: {matches[0]['disease']['name']}")
except Exception as e:
    print(f"    [FAIL] Pest Agent error: {e}")

# 7. Test Advisory Agent (data only)
print("\n[7] Testing Advisory Agent (seed varieties)...")
try:
    from agents.advisory_agent import SEED_VARIETIES, CROP_CALENDAR
    print(f"    [OK] Seed variety data: {len(SEED_VARIETIES)} crops")
    print(f"    [OK] Crop calendar data: {len(CROP_CALENDAR)} crops")
    wheat_vars = SEED_VARIETIES.get("wheat", [])
    print(f"    [OK] Wheat varieties: {len(wheat_vars)} options")
except Exception as e:
    print(f"    [FAIL] Advisory Agent error: {e}")

# 8. Test Orchestrator initialization
print("\n[8] Testing Orchestrator initialization...")
try:
    from agents.orchestrator import SmartFarmingOrchestrator, FarmerProfile
    orch = SmartFarmingOrchestrator()
    profile = FarmerProfile(
        name="Test Farmer",
        location="Pune",
        crops=["Soybean", "Cotton"],
        land_area_ha=2.0,
        soil_type="black",
        irrigation=True,
    )
    orch.set_farmer_profile(profile)
    print(f"    [OK] Orchestrator initialized")
    print(f"    [OK] Farmer profile set: {profile.to_context_string()}")

    # Test query classification
    test_queries = [
        ("Should I irrigate my soybean today?", "weather_irrigation"),
        ("My crop has brown spots and yellow leaves", "pest_disease"),
        ("What is the best selling price for cotton?", "market_insights"),
        ("How much fertilizer should I apply to wheat?", "advisory"),
    ]
    print("\n    Testing query routing:")
    for q, expected in test_queries:
        classified = orch.classify_query(q)
        status = "✅" if classified == expected else "⚠️ "
        print(f"    {status} '{q[:45]}...' → {classified}")

    # Test dashboard (no LLM)
    print("\n    Testing dashboard data fetch...")
    dashboard = orch.get_comprehensive_dashboard()
    print(f"    [OK] Dashboard data: {list(dashboard.keys())}")

except Exception as e:
    print(f"    [FAIL] Orchestrator error: {e}")

# 9. Test IBM Granite connection
print("\n[9] Testing IBM Granite LLM connection...")
try:
    import granite_client
    token = granite_client._get_cached_token()
    print(f"    [OK] IAM token obtained (length: {len(token)} chars)")
    print("    [INFO] Full LLM test skipped in automated test (use app.py for full test)")
except Exception as e:
    print(f"    [WARN] IAM token error (check API key): {e}")

print("\n" + "=" * 60)
print("  Test Summary Complete")
print("  Run 'streamlit run app.py' to launch the full application")
print("=" * 60)

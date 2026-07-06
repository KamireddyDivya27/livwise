"""
LivWise — AI Household & Community Living Advisor
Gen AI Academy APAC Edition | Challenge: AI for Better Living and Smarter Communities

A data-intelligence tool that compares a household's electricity & water usage
against real community benchmarks, then uses Google's Gemini model to turn that
comparison into fast, personalized, actionable recommendations.
"""

import os
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import google.generativeai as genai

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
st.set_page_config(page_title="LivWise — Smarter Living Advisor", page_icon="🏡", layout="wide")

# TEMP: paste your Gemini API key here for quick local testing only.
# Leave this as "" before you deploy — on Streamlit Cloud you'll set the real
# key via App settings -> Secrets instead, which is the secure way to do it.
LOCAL_API_KEY_FOR_TESTING = ""

def _get_secret_key():
    try:
        return st.secrets.get("GEMINI_API_KEY", None)
    except Exception:
        return None

API_KEY = LOCAL_API_KEY_FOR_TESTING or os.environ.get("GEMINI_API_KEY") or _get_secret_key()

@st.cache_data
def load_data():
    return pd.read_csv("community_benchmark.csv")

df = load_data()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🏡 LivWise — AI Household & Community Living Advisor")
st.caption(
    "Turn your monthly electricity & water bills into instant, data-backed decisions. "
    "Built for the Gen AI Academy APAC Edition — *AI for Better Living and Smarter Communities*."
)

if not API_KEY:
    st.warning(
        "No Gemini API key found. Add `GEMINI_API_KEY` under Streamlit secrets "
        "(or as an environment variable) to enable AI-generated recommendations. "
        "The benchmark comparison below still works without it.",
        icon="⚠️",
    )
else:
    genai.configure(api_key=API_KEY)

# ---------------------------------------------------------------------------
# Sidebar — user input
# ---------------------------------------------------------------------------
st.sidebar.header("Tell us about your household")

city = st.sidebar.selectbox("City", sorted(df["city"].unique()))
household_size = st.sidebar.slider("Household size (people)", 1, 5, 3)
electricity_kwh = st.sidebar.number_input("Last month's electricity usage (kWh)", min_value=0, value=250)
electricity_cost = st.sidebar.number_input("Last month's electricity bill (₹)", min_value=0, value=2000)
water_liters = st.sidebar.number_input("Last month's water usage (liters)", min_value=0, value=10000)
water_cost = st.sidebar.number_input("Last month's water bill (₹)", min_value=0, value=200)

analyze = st.sidebar.button("🔍 Analyze my household", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Analysis engine (the "data intelligence" core)
# ---------------------------------------------------------------------------
def get_benchmark(city, household_size):
    row = df[(df["city"] == city) & (df["household_size"] == household_size)]
    if row.empty:
        row = df[df["household_size"] == household_size]
    return row.iloc[0]


def pct_diff(user_value, benchmark_value):
    if benchmark_value == 0:
        return 0
    return round(((user_value - benchmark_value) / benchmark_value) * 100, 1)


def render_gauge(title, user_value, benchmark_value, unit):
    diff = pct_diff(user_value, benchmark_value)
    color = "#2C5F2D" if diff <= 0 else ("#F9E795" if diff <= 20 else "#F96167")
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=user_value,
        delta={"reference": benchmark_value, "relative": False},
        title={"text": f"{title} ({unit})"},
        gauge={
            "axis": {"range": [0, max(user_value, benchmark_value) * 1.4]},
            "bar": {"color": color},
            "threshold": {
                "line": {"color": "black", "width": 3},
                "thickness": 0.8,
                "value": benchmark_value,
            },
        },
    ))
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=50, b=10))
    return fig


def build_prompt(city, household_size, electricity_kwh, electricity_cost,
                  water_liters, water_cost, bench):
    return f"""
You are a friendly, practical smart-living advisor for a community energy & water
efficiency app called LivWise. Analyze this household's monthly resource use versus
their city's community benchmark, and respond in a clear, encouraging tone.

Household details:
- City: {city}
- Household size: {household_size}
- Electricity usage: {electricity_kwh} kWh (bill: ₹{electricity_cost})
- Water usage: {water_liters} liters (bill: ₹{water_cost})

Community benchmark for similar households in {city}:
- Avg electricity usage: {bench['avg_monthly_electricity_kwh']} kWh (avg bill ₹{bench['avg_monthly_electricity_cost_inr']})
- Avg water usage: {bench['avg_monthly_water_liters']} liters (avg bill ₹{bench['avg_monthly_water_cost_inr']})

Please provide:
1. A one-paragraph plain-English summary of how this household compares to their community.
2. Three specific, actionable recommendations (bulleted), each with an estimated
   monthly savings in ₹ or resource units where reasonable.
3. One "smarter community" insight — something this household could share with
   neighbors or local authorities to help the wider community save resources.

Keep the total response under 220 words. Do not use markdown headers, just bold labels and bullets.
"""


def get_ai_recommendation(prompt):
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text


# ---------------------------------------------------------------------------
# Main panel
# ---------------------------------------------------------------------------
if analyze:
    bench = get_benchmark(city, household_size)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            render_gauge("Electricity", electricity_kwh, bench["avg_monthly_electricity_kwh"], "kWh"),
            use_container_width=True,
        )
    with col2:
        st.plotly_chart(
            render_gauge("Water", water_liters, bench["avg_monthly_water_liters"], "liters"),
            use_container_width=True,
        )

    elec_diff = pct_diff(electricity_kwh, bench["avg_monthly_electricity_kwh"])
    water_diff = pct_diff(water_liters, bench["avg_monthly_water_liters"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Electricity vs community", f"{elec_diff:+.1f}%")
    c2.metric("Water vs community", f"{water_diff:+.1f}%")
    c3.metric("Your monthly bills", f"₹{electricity_cost + water_cost}")
    c4.metric("Community avg bills", f"₹{bench['avg_monthly_electricity_cost_inr'] + bench['avg_monthly_water_cost_inr']}")

    st.divider()
    st.subheader("🤖 AI-generated recommendations")

    if API_KEY:
        with st.spinner("LivWise is analyzing your household..."):
            try:
                prompt = build_prompt(city, household_size, electricity_kwh, electricity_cost,
                                       water_liters, water_cost, bench)
                recommendation = get_ai_recommendation(prompt)
                st.markdown(recommendation)
            except Exception as e:
                st.error(f"Couldn't reach Gemini API: {e}")
    else:
        st.info("Add your Gemini API key in secrets to unlock AI-generated recommendations here.")

    st.divider()
    st.caption(
        "Benchmark data is a sample community dataset for demo purposes. "
        "In production, LivWise would connect to real smart-meter / utility board data via BigQuery."
    )
else:
    st.info("👈 Enter your household details in the sidebar and click **Analyze my household** to get started.")
    st.markdown("""
    ### How LivWise works
    1. **You enter** your last month's electricity & water usage.
    2. **LivWise compares** it instantly against real community benchmark data for your city.
    3. **Gemini generates** a personalized, plain-English breakdown with concrete actions and estimated savings.
    4. **You decide faster** — no more guessing whether your bill is "normal" or where to cut back first.
    """)
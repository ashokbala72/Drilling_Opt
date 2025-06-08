
import streamlit as st
import pandas as pd
import plotly.express as px
import random
import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Drilling Optimization Assistant", layout="wide")
st.markdown("## Drilling Optimization Assistant")

# Define tabs
(
    overview_tab,
    realtime_tab,
    tuning_tab,
    bitwear_tab,
    cost_tab,
    feed_tab,
    dashboard_tab,
    recommendation_tab,
    ask_tab
) = st.tabs([
    "📌 Overview",
    "🛠️ Real-Time Drilling View",
    "🎛️ Auto Parameter Tuning",
    "🪓 Bit Wear Monitoring",
    "💰 Efficiency & Cost Tracker",
    "🔄 Real-Time Data Feed",
    "📊 Performance Dashboard",
    "📌 GenAI Recommendations",
    "❓ Ask a Query"
])


with overview_tab:
    st.header("📌 Overview: Drilling Optimization Assistant")

    st.markdown("""
### 🔍 What This App Does:

This assistant provides real-time and AI-enhanced insights across different aspects of a drilling operation using live or simulated sensor data.

#### 📊 Tab Guide:
- **🛠️ Real-Time Drilling View** – Live visualization of drilling parameters (ROP, WOB, RPM, Torque, Mud Flow), with GenAI suggestions.
- **🎛️ Auto Parameter Tuning** – Shows AI-suggested adjustments to improve drilling efficiency (e.g., WOB, RPM, Mud Flow).
- **🪓 Bit Wear Monitoring** – Displays bit wear levels and torque with trend graph and alerts.
- **💰 Efficiency & Cost Tracker** – Tracks cost per foot, NPT hours, and fuel usage along with visual KPIs.
- **🔄 Real-Time Data Feed** – Simulated sensor feed of WOB, RPM, Torque with GenAI interpretation.
- **📊 Performance Dashboard** – High-level KPIs showing stability, ROP variance, and downtime.
- **📌 GenAI Recommendations** – Consolidated AI-generated insights based on real-time data across the app.
- **❓ Ask a Query** – Free-form GenAI interface that answers user questions using all sensor data and system state.

---

### 🚀 How to Deploy This System in Production (Layman Steps):

1. **Prepare the Data Feed:**
   - Connect real-time sensor data APIs or SCADA systems (instead of simulated CSVs).
   - Ensure timestamps and sensor labels match expected format (WOB, RPM, etc.).

2. **Secure the Environment:**
   - Store your OpenAI API key securely (e.g., environment variables or secrets manager).
   - Use HTTPS endpoints and authentication for accessing drilling data.

3. **Deploy the Application:**
   - Use a platform like **Streamlit Community Cloud**, **Heroku**, **AWS EC2**, or **Azure App Services**.
   - Install required Python libraries using `requirements.txt`.

4. **Enable Monitoring:**
   - Add logging, health checks, and exception handling for GenAI and data ingestion.
   - Use dashboards to visualize latency or API failures.

5. **Test with Real Data:**
   - Begin with a sandbox data set from your operations team.
   - Tune thresholds and alerts based on real-world drilling outcomes.

6. **Train Your Team:**
   - Explain what each tab shows, how to interpret GenAI insights.
   - Create workflows to act on recommendations (bit replacement, parameter tuning, etc.).

7. **Iterate & Improve:**
   - Gather feedback from field engineers and drilling analysts.
   - Add new features like report export, mobile views, or multi-site comparisons.
    """)

with realtime_tab:
    st.title("🛠️ Unified Drilling Optimization Assistant")
    drilling_type = st.sidebar.selectbox("Select Drilling Type", ["Oil & Gas", "Mining", "Geothermal"])
    refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 5, 30, 10)
    auto_refresh = st.sidebar.checkbox("Enable Auto Refresh", value=True)

    file_map = {
        "Oil & Gas": "sensor_data_oil_&_gas.csv",
        "Mining": "sensor_data_mining.csv",
        "Geothermal": "sensor_data_geothermal.csv"
    }

    df = pd.read_csv(file_map[drilling_type])
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    st.subheader(f"📊 Sensor Trends for {drilling_type}")
    st.line_chart(df.set_index("Timestamp")[["ROP_ft_per_hr", "WOB_klbf", "RPM"]])

    latest = df.tail(1).iloc[0]
    if latest["ROP_ft_per_hr"] < 8 and latest["Torque_lbf_ft"] > 500:
        st.warning("⚠️ Low ROP and high torque! Check bit wear or WOB setting.")
    elif latest["Mud_Flow_gpm"] < 250:
        st.warning("⚠️ Mud flow is low. Monitor hole cleaning.")
    else:
        st.success("✅ Parameters within normal range.")

    st.subheader("🧠 Generate AI Optimization Advice")
    summary = f"""Latest drilling parameters for {drilling_type}:
- Bit Depth: {latest['Bit_Depth_ft']} ft
- ROP: {latest['ROP_ft_per_hr']} ft/hr
- WOB: {latest['WOB_klbf']} klbf
- RPM: {latest.get('RPM', 130)}
- Torque: {latest['Torque_lbf_ft']} lbf-ft
- Mud Flow: {latest['Mud_Flow_gpm']} gpm
- Formation: {latest['Formation']}

Based on this data, suggest optimization actions, root causes, and adjustments."""

    if st.button("🔍 AI Recommendations"):
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": summary}]
                )
                st.text_area("💡 AI Optimization Advice", response.choices[0].message.content, height=240)
        except Exception as e:
            st.error(f"❌ OpenAI API call failed: {e}")

    st.subheader("📋 Last 10 Records")
    st.dataframe(df.tail(10))

with tuning_tab:
    st.subheader("🎛️ Auto Parameter Tuning")
    st.markdown("AI-recommended changes to drilling parameters:")
    tuning_data = {
        "Weight on Bit (WOB)": ["22,000 lbs", "24,000 lbs"],
        "Rotary Speed (RPM)": ["120", "135"],
        "Mud Flow Rate (gpm)": ["450", "480"]
    }
    st.table(pd.DataFrame(tuning_data, index=["Original", "AI-Tuned"]).T)
    if st.checkbox("Apply AI-Tuned Parameters to Next Cycle"):
        st.success("✔️ Parameters will be used for next simulation cycle.")

with bitwear_tab:
    st.subheader("🪓 Bit Wear Monitoring")
    torque = random.randint(18000, 23000)
    wear = random.randint(60, 90)
    st.metric("Bit Wear %", f"{wear}%", delta=f"{-random.randint(1,5)}%")
    st.metric("Torque", f"{torque} ft-lbf")
    if wear > 80:
        st.warning("⚠️ Bit nearing critical wear level.")
    st.markdown("🧠 **GenAI Insight**: Bit wear increasing due to abrasive zone at 3100 ft.")

    wear_history = pd.DataFrame({
        "Timestamp": pd.date_range(end=pd.Timestamp.now(), periods=5, freq="T"),
        "Bit Wear (%)": [60, 65, 70, 78, wear],
        "Torque": [19000, 19500, 20000, 21000, torque]
    })
    st.dataframe(wear_history)
    st.line_chart(wear_history.set_index("Timestamp")[["Bit Wear (%)", "Torque"]])


with cost_tab:
    st.subheader("💰 Efficiency & Cost Tracker")
    st.metric("Cost per Foot", "$29.75", delta="-2.4%")
    st.metric("NPT (hrs)", "1.6", delta="-0.2")
    st.metric("Fuel Usage", "1250 gal/day")
    st.info("🧠 **GenAI Suggestion**: Maintain current RPM. Reuse mud to lower cost by 5%.")

    cost_data = pd.DataFrame({
        "Metric": ["Cost per Foot", "NPT (hrs)", "Fuel Usage"],
        "Value": [29.75, 1.6, 1250]
    })
    fig = px.bar(cost_data, x="Metric", y="Value", title="Efficiency & Cost Metrics")
    st.plotly_chart(fig, use_container_width=True)





with feed_tab:
    st.subheader("🔄 Real-Time Data Feed")

    if "feed_history" not in st.session_state:
        now = pd.Timestamp.now()
        st.session_state.feed_history = [
            {
                "WOB": random.randint(18000, 23000),
                "RPM": random.randint(110, 150),
                "Torque": random.randint(17000, 21000),
                "Timestamp": now - pd.Timedelta(seconds=50 - 5 * i)
            }
            for i in range(10)
        ]

    df_feed = pd.DataFrame(st.session_state.feed_history)
    st.dataframe(df_feed)



    
    st.subheader("🧠 GenAI Interpretation")
    insight_prompt = f"""Current drilling sensor readings:

- WOB: {latest.get('WOB', 22000)} lbs
- RPM: {latest.get('RPM', 130)}
- Torque: {latest.get('Torque', 21000)} ft-lbf

Provide insights into current operational efficiency and risks.
Suggest improvements based on these values.
"""
    if st.button("🧠 Get GenAI Insight"):
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            with st.spinner("Analyzing..."):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": insight_prompt}]
                )
                st.success("✅ AI Insight Ready")
                st.markdown(response.choices[0].message.content)
        except Exception as e:
            st.error(f"❌ GenAI failed: {str(e)}")

    latest = df_feed.iloc[-1]
    st.write(f"**Latest Readings:** WOB: {latest.get('WOB', 22000)} lbs | RPM: {latest.get('RPM', 130)} | Torque: {latest.get('Torque', 21000)} ft-lbf")

    if latest["Torque"] > 20000:
        st.error("⚠️ Torque high – risk of overloading motor.")
    else:
        st.success("✅ Feed within expected range.")



with dashboard_tab:
    st.subheader("📊 Performance Dashboard")
    st.metric("ROP Variance", "Low")
    st.metric("Stability Index", "0.91")
    st.metric("NPT %", "6.2%")
    st.markdown("🧠 **GenAI Insight**: Drilling stable. Slight torque variance, no critical risk.")

    performance_data = {
        "ROP Variance": 0.3,
        "Stability Index": 0.91,
        "NPT %": 6.2
    }
    st.bar_chart(pd.DataFrame(performance_data.items(), columns=["Metric", "Value"]).set_index("Metric"))





with recommendation_tab:
    st.subheader("📌 Consolidated GenAI Recommendations")

    # Pull session or simulate data
    bit_wear = st.session_state.get("bit_wear", random.randint(75, 90))
    torque = st.session_state.get("torque", random.randint(20000, 22000))
    cost_per_foot = 29.75
    npt_hours = 1.6
    latest_feed = st.session_state.get("feed_history", [])
    if latest_feed:
        latest = latest_feed[-1]
        wob = latest.get("WOB", 22000)
        rpm = latest.get("RPM", 130)
        rt_torque = latest.get("Torque", torque)
    else:
        wob, rpm, rt_torque = 22000, 130, torque

    prompt = f"""Current drilling performance summary:

- Bit Wear: {bit_wear}%
- Torque: {torque} ft-lbf
- Cost per Foot: ${cost_per_foot}
- NPT: {npt_hours} hrs
- Real-time WOB: {wob} lbs
- RPM: {rpm}
- Real-time Torque: {rt_torque} ft-lbf

Based on this, what are the key risks, optimization opportunities, and recommended actions to improve drilling efficiency?
"""

    if st.button("🧠 Generate Consolidated Recommendations"):
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            with st.spinner("Generating recommendations..."):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.success("✅ Recommendations Ready")
                st.markdown(response.choices[0].message.content)
        except Exception as e:
            st.error(f"❌ GenAI failed: {str(e)}")




with ask_tab:
    st.subheader("❓ Ask a GenAI-Powered Question")

    # Pull session or simulate fallback data
    bit_wear = st.session_state.get("bit_wear", random.randint(75, 90))
    torque = st.session_state.get("torque", random.randint(20000, 22000))
    cost_per_foot = 29.75
    npt_hours = 1.6
    latest_feed = st.session_state.get("feed_history", [])
    if latest_feed:
        latest = latest_feed[-1]
        wob = latest.get("WOB", 22000)
        rpm = latest.get("RPM", 130)
        rt_torque = latest.get("Torque", torque)
    else:
        wob, rpm, rt_torque = 22000, 130, torque

    user_question = st.text_area("🗣️ Enter your question about drilling status or advice:")
    if st.button("🤖 Ask GenAI"):
        context = f"""Current Drilling Snapshot:

- Bit Wear: {bit_wear}%
- Torque: {torque} ft-lbf
- Cost per Foot: ${cost_per_foot}
- NPT: {npt_hours} hrs
- Real-time WOB: {wob} lbs
- RPM: {rpm}
- Real-time Torque: {rt_torque} ft-lbf

Question: {user_question}
"""
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": context}]
                )
                st.success("✅ Answer Ready")
                st.markdown(response.choices[0].message.content)
        except Exception as e:
            st.error(f"❌ GenAI failed: {str(e)}")


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
(overview_tab, realtime_tab, tuning_tab, bitwear_tab, cost_tab, dashboard_tab, recommendation_tab, ask_tab) = st.tabs(["📌 Overview", "🛠️ Unified Real-Time Drilling", "🎛️ Auto Parameter Tuning", "🪓 Bit Wear Monitoring", "💰 Efficiency & Cost Tracker", "📊 Performance Dashboard", "📌 GenAI Recommendations", "❓ Ask a Query"])





with overview_tab:
    st.header("📌 Overview: Drilling Optimization Assistant")
    st.markdown("""
This assistant helps drilling engineers and field operators monitor and optimize drilling operations using AI-powered insights and sensor data. It supports real-time monitoring, fault detection, cost optimization, and GenAI-driven decision support.

---

### 🔍 Data Sources: Mock vs Real-Time

- **Currently Simulated (Mock) Data**:
  - Sensor readings like WOB, Torque, RPM, Mud Flow, Bit Depth, Bit Wear, etc.
  - Fuel usage, cost per foot, and non-productive time (NPT) are simulated.
  - GenAI recommendations are generated live using the simulated context.

- **Can Be Made Real-Time By**:
  - Integrating rig SCADA systems, WITSML feeds, or APIs (e.g., AWS IoT, Azure IoT Hub)
  - Replacing internal simulator with data ingestion pipelines or sockets
  - Connecting formation logs, bit sensors, or BHA instrumentation feeds

---

### 📋 What Each Tab Does (in Layman Terms)

**🛠️ Unified Real-Time Drilling View**  
Shows live trends for Weight on Bit, Torque, RPM, Mud Flow, and Bit Depth.  
👉 Flags problems like:
- High Torque (bit stuck or hard formation)
- Low Mud Flow (potential pump failure)
- Sudden ROP drops (inefficient drilling)

**🎛️ Auto Parameter Tuning**  
Automatically compares your actual drilling settings with ideal AI-tuned values.  
👉 Helps reduce wear, fuel, and improve penetration rate.

**🪓 Bit Wear Monitoring**  
Tracks how much the drill bit has worn out and when to replace it.  
👉 Prevents breakdowns and reduces risk of tool failure in-hole.

**💰 Efficiency & Cost Tracker**  
Shows the cost per foot drilled, fuel use, and how much time was lost (NPT).  
👉 Makes it easy to control budget and justify downtime.

**📊 Performance Dashboard**  
Visual summary of overall system performance using KPIs like:
- ROP Variance: Is drilling smooth or inconsistent?
- Stability Index: Is the drill string stable?
- NPT %: How much time is being lost?

**📌 GenAI Recommendations**  
Uses GPT to generate smart suggestions like:
👉 “Increase RPM slightly to match formation hardness”  
👉 “Consider bit replacement within next 500 ft”

**❓ Ask a Query**  
Type a question (e.g., “Why is torque increasing suddenly?”)  
👉 Get an AI-generated explanation based on current data.

---

### 🛠️ Deployment Note:
Use the drilling type selector (Oil & Gas, Mining, Geothermal) to adapt the assistant for different scenarios. All tabs support both mock and real-time integration depending on feed availability.
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

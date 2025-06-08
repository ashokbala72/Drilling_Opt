import streamlit as st
import random
import pandas as pd
st.set_page_config(page_title="Drilling Optimization Assistant", layout="wide")

tabs = st.tabs([
    "📌 Overview",
    "🛠️ Main Assistant",
    "🧠 Auto Parameter Tuning",
    "🔩 Bit Wear Monitor",
    "📉 Efficiency & Cost Tracker",
    "🌐 Real-Time Data Feed Setup",
    "📊 Performance Dashboard"
])


import plotly.express as px
from openai import OpenAI
import os
import time
from dotenv import load_dotenv
load_dotenv()


# Add overview as a separate tab


with tabs[0]:

    st.markdown("""
    ## 🛠️ Drilling Optimization – Exploration and Real-Time Efficiency Assistant
    
    This intelligent application helps drilling engineers and operations teams make better, faster decisions by simulating and optimizing every part of the drilling process. Below is an easy-to-understand walkthrough of what this app does:
    
    ---
    
    ### 🔍 What Does This App Do?
    
    1. **Overview Tab (You're here!)**  
       Explains the entire app in simple terms. Think of this as the user manual in plain language.
    
    2. **Real-Time Drilling View**  
       Shows the current drilling status like where you're drilling (location), how deep you've gone, and geological conditions. Useful for staying on top of field operations.
    
    3. **Auto Parameter Tuning**  
       AI adjusts your drilling settings like how hard to press the drill (WOB), how fast it should rotate (RPM), and how much mud to use. This helps save cost and drill faster.
    
    4. **Bit Wear Monitoring**  
       Tells you how much the drill bit is worn out. Prevents damage and helps decide when to replace the bit.
    
    5. **Efficiency & Cost Tracker**  
       Tracks how efficiently you're drilling and how much it's costing per foot. Helps reduce unnecessary delays and costs.
    
    6. **Real-Time Data Feed**  
       Simulates a live sensor feed like from SCADA or WITSML. It shows drilling values like torque and RPM in real time. Warnings are shown if values cross dangerous thresholds. You can refresh the feed manually.
    
    7. **Performance Dashboard**  
       A snapshot of overall performance including drilling stability, non-productive time (NPT), and how variable the drilling speed (ROP) is. Includes GenAI insights for better decision-making.
    
    ---
    
    ### 🧠 How Does AI Help?
    
    - Suggests optimized drilling parameters
    - Warns about risks from abnormal torque/WOB
    - Recommends when to replace worn tools
    - Provides explanations for what’s happening based on sensor data
    
    ---
    
    ### 💡 What Can Be Made Real?
    
    Currently, some parts are mocked (simulated), but they can be made real by:
    - Connecting to live WITSML feeds (for real-time data)
    - Integrating with SCADA or rig control systems
    - Using real drilling logs and surface sensor data
    - Connecting to a live AI/ML backend trained on your drilling history
    
    This app is designed to scale with your real data. Use it now as a simulation, or connect to your field assets to go fully operational.
    

---

### 🚀 How to Deploy This in Production

To run this Drilling Optimization Assistant in a production-grade environment:

1. **Backend Integration**
   - Replace the simulated telemetry feed with a real WITSML/SCADA API.
   - Ensure secure API tokens or OAuth for accessing live drilling rigs.
   - Use a time-series database (e.g., InfluxDB or TimescaleDB) for storing telemetry.

2. **AI & ML Integration**
   - Replace GenAI stubs with a production-grade GPT/LLM endpoint or trained model.
   - Fine-tune models using your own drilling history for better performance.

3. **UI & Hosting**
   - Package this Streamlit app using Docker or deploy to Streamlit Community Cloud.
   - For high-availability, use cloud platforms like Azure, AWS, or GCP with Streamlit sharing, or run behind a reverse proxy like NGINX.
   - Use HTTPS and authentication (e.g., Azure AD, Okta) for access control.

4. **Monitoring & Logging**
   - Integrate logging using Python’s `logging` module or services like ELK stack.
   - Add usage monitoring and alerts for performance anomalies.

5. **Data Privacy & Security**
   - Ensure no PII is logged or shared.
   - Encrypt data in transit and at rest.
   - Review and comply with drilling operation security standards.

This app is designed to scale — use this simulated version to test features and then plug in your real services.
    """)
    
    
with tabs[1]:
        st.title("🛠️ Unified Drilling Optimization Assistant")
        # Sidebar controls
        drilling_type = st.sidebar.selectbox("Select Drilling Type", ["Oil & Gas", "Mining", "Geothermal"])
        refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 5, 30, 10)
        auto_refresh = st.sidebar.checkbox("Enable Auto Refresh", value=True)
        # File map
        file_map = {
        "Oil & Gas": "sensor_data_oil_&_gas.csv",
        "Mining": "sensor_data_mining.csv",
        "Geothermal": "sensor_data_geothermal.csv"
        }
        # Load and prepare data
        df = pd.read_csv(file_map[drilling_type])
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        # Plot sensor data
        st.subheader(f"📊 Sensor Trends for {drilling_type}")
        st.line_chart(df.set_index("Timestamp")[["ROP_ft_per_hr", "WOB_klbf", "RPM"]])
        # Alert logic
        latest = df.tail(1).iloc[0]
        if latest["ROP_ft_per_hr"] < 8 and latest["Torque_lbf_ft"] > 500:
            st.warning("⚠️ Low ROP and high torque! Check bit wear or WOB setting.")
        elif latest["Mud_Flow_gpm"] < 250:
            st.warning("⚠️ Mud flow is low. Monitor hole cleaning.")
        else:
            st.success("✅ Parameters within normal range.")
        # AI Insight section
        st.subheader("🧠 Generate AI Optimization Advice")
        summary = (
        f"Latest drilling parameters for {drilling_type}:\n"
        f"- Bit Depth: {latest['Bit_Depth_ft']} ft\n"
        f"- ROP: {latest['ROP_ft_per_hr']} ft/hr\n"
        f"- WOB: {latest['WOB_klbf']} klbf\n"
        f"- RPM: {latest['RPM']}\n"
        f"- Torque: {latest['Torque_lbf_ft']} lbf-ft\n"
        f"- Mud Flow: {latest['Mud_Flow_gpm']} gpm\n"
        f"- Formation: {latest['Formation']}\n\n"
        "Based on this data, suggest optimization actions, root causes, and adjustments."
        )
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
            # Show last 10 records
            st.subheader("📋 Last 10 Records")
            st.dataframe(df.tail(10))
            # Trigger auto-refresh AFTER rendering
            if auto_refresh:
                time.sleep(refresh_interval)
                st.query_params = {"r": str(int(st.query_params.get("r", "0")) + 1)}
                st.rerun()
            



with tabs[2]:
    st.header("🧠 Auto Parameter Tuning")
    st.markdown("AI-tuned drilling parameters for current depth and formation:")

    tuning_data = {
        "Weight on Bit (WOB)": ["20,000 lbs", "22,500 lbs"],
        "Rotary Speed (RPM)": ["120 RPM", "135 RPM"],
        "Mud Flow Rate": ["450 gpm", "470 gpm"],
        "Differential Pressure": ["400 psi", "420 psi"]
    }

    df = pd.DataFrame.from_dict(tuning_data, orient='index', columns=["Original", "AI-Tuned"])
    st.table(df)

    apply_changes = st.checkbox("Apply AI-recommended drilling parameters to next cycle", key="auto_tune")
    if apply_changes:
        st.success("AI-tuned parameters will be simulated in the next drill cycle.")



with tabs[3]:
    st.header("🔩 Bit Wear Monitoring")
    st.markdown("Real-time estimates of bit wear and health using operational telemetry.")

    st.subheader("📊 Bit Health Metrics")
    st.metric("Bit Condition", "Moderate", delta="-5% from last hour")
    st.metric("Cumulative Drilled Length", "3,850 ft")
    st.metric("Average Torque", "18,500 ft-lbf")

    st.subheader("🧠 GenAI Insight")
    st.info("Bit wear shows progressive degradation due to abrasive sandstone layer. Consider pulling out at 4,200 ft for inspection.")

    st.line_chart({
        "Time (min)": list(range(10)),
        "Wear Index": [92, 90, 89, 87, 84, 82, 80, 78, 76, 75]
    })


with tabs[4]:
    st.header("📉 Efficiency & Cost Tracker")
    st.markdown("Live tracking of operational efficiency and cost indicators.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Cost per Foot", "$27.40", "-3.2%")
    col2.metric("Drilling Time per 100ft", "15 min", "-5%")
    col3.metric("Fuel Consumption", "1200 gal/day", "Stable")

    st.subheader("🧠 GenAI Insight")
    st.info("Reduced slide drilling time by 8% using consistent RPM and mud density. Opportunity to cut cost further by 6% using recycled mud.")

    st.bar_chart({
        "Metric": ["Cost/ft", "Time/100ft", "Fuel"],
        "Value": [27.4, 15, 1200]
    })






with tabs[5]:
    st.header("🌐 Real-Time Data Feed Setup")
    st.markdown("Simulated real-time drilling telemetry data feed. Values refresh automatically on page load or manually.")

    # Generate new simulated reading
    wob = random.randint(18000, 23000)
    rpm = random.randint(110, 140)
    torque = random.randint(17000, 20000)
    depth = random.randint(3500, 4200)
    st.session_state['feed_data'] = {
        "WOB (lbs)": wob,
        "RPM": rpm,
        "Torque (ft-lbf)": torque,
        "Depth (ft)": depth
    }

    # Initialize or update telemetry history
    if 'telemetry_history' not in st.session_state:
        st.session_state['telemetry_history'] = []

    st.session_state['telemetry_history'].append({
        "WOB": wob,
        "RPM": rpm,
        "Torque": torque
    })
    st.session_state['telemetry_history'] = st.session_state['telemetry_history'][-20:]

    data = st.session_state['feed_data']
    st.metric("Weight on Bit (WOB)", f"{data['WOB (lbs)']} lbs")
    st.metric("Rotary Speed (RPM)", f"{data['RPM']} RPM")
    st.metric("Torque", f"{data['Torque (ft-lbf)']} ft-lbf")
    st.metric("Current Depth", f"{data['Depth (ft)']} ft")

    # Alert conditions
    if data['WOB (lbs)'] > 22500:
        st.error("⚠️ WOB exceeds safe threshold! Risk of bit damage.")
    if data['Torque (ft-lbf)'] > 19500:
        st.warning("⚠️ High torque levels. Watch for vibration or bit wear.")
    st.subheader("🧠 GenAI Recommendation")
    st.info("Telemetry is stable. Slight increase in torque noted. If sustained, consider adjusting RPM or reduce WOB for smoother drilling.")


with tabs[6]:
    st.header("📊 Performance Dashboard")
    st.markdown("Summary of real-time drilling KPIs and trend analysis.")

    col1, col2, col3 = st.columns(3)
    col1.metric("NPT %", "7.8%", "-0.6%")
    col2.metric("Stability Index", "0.91", "+2.3%")
    col3.metric("ROP Variability", "Low", "Stable")

    st.subheader("🧠 GenAI Summary")
    st.info("Operation is stable. Slight torque fluctuations seen in shale region. Consider adjusting RPM for smoother bit rotation.")

    import numpy as np
    df = pd.DataFrame({
        "Depth": np.arange(1000, 5000, 500),
        "ROP": [22, 25, 28, 21, 23, 27, 26, 29]
    })
    st.line_chart(df.set_index("Depth"))

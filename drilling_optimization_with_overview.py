import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI
import os
import time
from dotenv import load_dotenv
load_dotenv()


# Add overview as a separate tab
st.set_page_config(page_title="Drilling Optimization Assistant", layout="wide")
overview_tab, main_tab = st.tabs(["📌 Overview", "🛠️ Main Assistant"])

with overview_tab:
    st.header("📌 Overview: Drilling Optimization Assistant")
    st.markdown("""
### 🧾 Inputs Used:
- **Real-time sensor data** from drilling operations:
    - Rate of Penetration (ROP)
    - Weight on Bit (WOB)
    - RPM (rotations per minute)
    - Torque
    - Mud Flow
    - Bit Depth
    - Formation type

### 🔎 How the Inputs Are Reviewed:
- The assistant monitors sensor data trends via charts.
- Alerts are triggered when unsafe or suboptimal conditions are detected (e.g. low ROP with high torque).
- GenAI analyzes the latest sensor readings and offers improvement suggestions.

### 🚧 Faults Reported:
| Fault Type             | Layman Description                                 |
|------------------------|----------------------------------------------------|
| Low ROP + High Torque  | Drill bit is struggling to cut, might be dull     |
| Low Mud Flow           | Not enough cleaning fluid; debris may block hole  |
| Excessive WOB          | Too much weight can damage the bit                |
| Abnormal RPM           | Rotation speed too fast or slow affects drilling  |

### 🌟 Benefits Provided:
- Early identification of drilling inefficiencies or risks
- AI-generated advice for parameter adjustments
- Better bit life and faster drilling operations
- Safer and more cost-efficient drilling
    """)



# moved to main tab:
with main_tab:
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
            
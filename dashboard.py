import streamlit as st
import time
from streaming.producer import producer_pcap,get_data

st.set_page_config(page_title="Network Live Stream", layout="wide")
st.title("Real-time Packet Streaming & Analysis")

# 1. Create placeholders for the UI so they don't jump around
status_text = st.empty()
data_display = st.empty()
log_display = st.empty()

# Add a "Stop" button in the sidebar
run_analysis = st.sidebar.button("Start Live Capture")
stop_analysis = st.sidebar.button("Stop")
attack_summary=st.sidebar.button("Attack Summary")
    
if attack_summary:
    st.write("### 🚨 Attack Details")
    st.table(get_data())
if run_analysis:
    st.sidebar.success("Streaming Active")
    
    # The Live Loop
    while True:
        status_text.info("📡 Capturing  packets...")
        
        # 2. Get results from your producer
        results = producer_pcap(packet_count=60)
        
        # 3. Update the UI without refreshing the whole page
        with data_display.container():
            col1, col2, col3 = st.columns(3)
            col1.metric("Normal Traffic", results["normal_count"])
            col2.metric("Attacks Detected", results["attack_count"], delta_color="inverse")
            col3.metric("Model Status", "Healthy" if "healthy" in results["model_health"] else "Alert")

            # 3. Attacks List
            st.write("### 🚨 Attack Details")
            if not results["attacks"]:
                st.info("No active attacks detected in this batch.")
            else:
                st.table(results["attacks"])

            # 4. Footer
            
        with log_display.container():
            st.write(f"Last updated: {time.strftime('%H:%M:%S')}")

        # Small delay to prevent Streamlit from freezing
        time.sleep(1) 
        
        if stop_analysis:
            st.sidebar.warning("Stream Stopped")
            break
else:
    st.info("Click 'Start Live Capture' to begin.")

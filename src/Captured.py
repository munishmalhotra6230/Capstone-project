from scapy.all import rdpcap, IP, TCP, UDP
import pandas as pd
import numpy as np
from collections import defaultdict

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.pipeline import Full_pipeline

def extract_features(pkts):
    sizes = [len(p) for p in pkts]
    times = [float(p.time) for p in pkts]
    iats = np.diff(times).tolist() if len(times) > 1 else [0]
    
    fwd = pkts[:len(pkts)//2]
    bwd = pkts[len(pkts)//2:]
    fwd_sizes = [len(p) for p in fwd] or [0]
    bwd_sizes = [len(p) for p in bwd] or [0]

    syn = sum(1 for p in pkts if TCP in p and p[TCP].flags & 0x02)
    fin = sum(1 for p in pkts if TCP in p and p[TCP].flags & 0x01)
    psh = sum(1 for p in pkts if TCP in p and p[TCP].flags & 0x08)
    ack = sum(1 for p in pkts if TCP in p and p[TCP].flags & 0x10)
    urg = sum(1 for p in pkts if TCP in p and p[TCP].flags & 0x20)

    duration = times[-1] - times[0] if len(times) > 1 else 0.001
    
    import datetime
    start_time = datetime.datetime.fromtimestamp(times[0]).strftime('%Y-%m-%d %H:%M:%S')

    return {
        'Timestamp':                 start_time,
        'Destination Port':          pkts[0][TCP].dport if TCP in pkts[0] else 0,
        'Flow Duration':             duration * 1e6,
        'Total Length of Fwd Packets': sum(fwd_sizes),
        'Fwd Packet Length Mean':    np.mean(fwd_sizes),
        'Fwd Packet Length Std':     np.std(fwd_sizes),
        'Bwd Packet Length Mean':    np.mean(bwd_sizes),
        'Bwd Packet Length Std':     np.std(bwd_sizes),
        'Flow Bytes/s':              sum(sizes) / duration,
        'Flow Packets/s':            len(pkts) / duration,
        'Flow IAT Std':              np.std(iats),
        'Fwd IAT Total':             sum(iats),
        'Fwd IAT Mean':              np.mean(iats),
        'Fwd IAT Std':               np.std(iats),
        'Bwd IAT Total':             sum(iats),
        'Bwd IAT Mean':              np.mean(iats),
        'Bwd IAT Std':               np.std(iats),
        'Fwd PSH Flags':             psh,
        'Fwd Packets/s':             len(fwd) / duration,
        'Bwd Packets/s':             len(bwd) / duration,
        'Packet Length Mean':        np.mean(sizes),
        'Packet Length Std':         np.std(sizes),
        'FIN Flag Count':            fin,
        'SYN Flag Count':            syn,
        'PSH Flag Count':            psh,
        'ACK Flag Count':            ack,
        'URG Flag Count':            urg,
        'Down/Up Ratio':             len(bwd) / max(len(fwd), 1),
        'Avg Fwd Segment Size':      np.mean(fwd_sizes),
        'Avg Bwd Segment Size':      np.mean(bwd_sizes),
        'Subflow Fwd Bytes':         sum(fwd_sizes),
        'Init_Win_bytes_forward':    pkts[0][TCP].window if TCP in pkts[0] else 0,
        'Init_Win_bytes_backward':   pkts[-1][TCP].window if TCP in pkts[-1] else 0,
        'Active Std':                np.std(sizes),
        'Idle Mean':                 np.mean(iats),
        'Idle Std':                  np.std(iats),
    }

def analyze_pcap(pcap_file):
    print(f"Reading pcap file: {pcap_file}")
    packets = rdpcap(pcap_file)
    print(f"Total packets: {len(packets)}")

    flows = defaultdict(list)
    for pkt in packets:
        if IP in pkt:
            key = (pkt[IP].src, pkt[IP].dst, pkt[IP].proto)
            flows[key].append(pkt)

    records = []
    for key, pkts in flows.items():
        if len(pkts) >= 3:
            try:
                records.append(extract_features(pkts))
            except Exception as e:
                pass

    df = pd.DataFrame(records)
    print(f"Total flows extracted: {len(df)}")
    
    if not df.empty:
        Nids = Full_pipeline(df)
        result, confidence = Nids.run()
        
        # Inject Model Health Status
        from model_health.timebased import timebased_model_health
        total_flows = len(df)
        status = timebased_model_health(confidence, total_flows)
        result['model_health'] = status
        
        return result
    else:
        print("No valid flows found to analyze.")
        return {
            'normal_count': 0,
            'attack_count': 0,
            'attacks': [],
            'model_health': 'no data'
        }

def convert_pcap_to_csv(pcap_file, output_csv="output_traffic.csv"):
    """
    Utility feature to extract all flow metrics from a .pcap file
    and save it directly to a .csv for external training or inspection.
    """
    print(f"Reading pcap file to convert to CSV: {pcap_file}")
    from scapy.all import rdpcap, IP
    packets = rdpcap(pcap_file)
    
    flows = defaultdict(list)
    for pkt in packets:
        if IP in pkt:
            key = (pkt[IP].src, pkt[IP].dst, pkt[IP].proto)
            flows[key].append(pkt)

    records = []
    for key, pkts in flows.items():
        if len(pkts) >= 3:
            try:
                records.append(extract_features(pkts))
            except Exception:
                pass

    df = pd.DataFrame(records)
    if not df.empty:
        df.to_csv(output_csv, index=False)
        print(f"Success! {len(df)} flows saved to {output_csv}")
        return True
    else:
        print("Failed: No valid flows extracted.")
        return False

# Example usage if script is run directly:
if __name__ == "__main__":
    default_pcap = os.path.join(os.path.dirname(__file__), "traffic.pcapng")
    if os.path.exists(default_pcap):
        # By uncommenting the line below, you can convert pcaps locally!
        # convert_pcap_to_csv(default_pcap, output_csv="converted_traffic.csv")
        pass

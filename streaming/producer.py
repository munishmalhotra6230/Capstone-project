import sys
import os
from scapy.all import sniff, wrpcap
import tempfile

# Ensure project root is on sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.Captured import analyze_pcap

def producer_pcap(packet_count):

        print("\n[+] Capturing...")
        pca_file = sniff(count=packet_count)
        
        # 1. Create the temp file but close it immediately so it's not "in use"
        tmp = tempfile.NamedTemporaryFile(suffix=".pcapng", delete=False)
        tmp_path = tmp.name
        tmp.close() # Release the lock so Scapy can write to it
        
        try:
            # 2. Write packets to the path
            wrpcap(tmp_path, pca_file)
            
            # 3. Analyze
            results = analyze_pcap(tmp_path)
            print(f"Results: {results}")
            return results
            
        finally:
            # 4. MANUALLY delete the file after analysis to save memory/space
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                print("[✓] Temp file cleaned up.")



        


    

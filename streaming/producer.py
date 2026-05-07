import sys
import os
from scapy.all import sniff, wrpcap
import tempfile
import sqlite3
# def create_db():
#      con=sqlite3.connect(r"db_path/attacks.db")
#      con.execute("CREATE TABLE attack ( ID INT AUTO_INCREMENT PRIMARY KEY, IP_ADDRESS VARCHAR,ATTACK_TIME DATETIME ,TYPE VARCHAR(30) )")
#      con.commit()
#      con.close()
def insert(ip_address, time, type_):
    con = sqlite3.connect(r"db_path/attacks.db")
    con.execute(
        "INSERT INTO attack (IP_ADDRESS, ATTACK_TIME, TYPE) VALUES (?, ?, ?)",
        (ip_address, time, type_)
    )
    con.commit()
    con.close()
def get_data():
    con=sqlite3.connect(r"db_path/attacks.db")
    cursor=con.execute("SELECT * FROM attack")
    rows=cursor.fetchall()
    con.close()
    return rows    
     

# Ensure project root is on sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.Captured import analyze_pcap

def producer_pcap(packet_count):

        print("\n[+] Capturing...")
        pca_file = sniff(count=packet_count)
        
        # 1. Create the temp file but close it immediately so it's not in use

        tmp = tempfile.NamedTemporaryFile(suffix=".pcapng", delete=False)
        tmp_path = tmp.name
        tmp.close() # Release the lock so Scapy can write to it
        try:
            # 2. Write packets to the path
            wrpcap(tmp_path, pca_file)
            
            # 3. Analyze
            results = analyze_pcap(tmp_path)
            print(f"Results: {results}")
            
            # 4. Save each attack (with attacker IP) to the database
            attacks = results.get('attacks', [])
            if attacks:
                print(f"[DB] Saving {len(attacks)} attack(s) to database...")
                for entry in attacks:
                    ip, time, attack_type = entry
                    insert(ip, time, attack_type)
                    print(f"[DB] Inserted → IP: {ip} | Time: {time} | Type: {attack_type}")
            
            return results
            
        finally:
            # 4. MANUALLY delete the file after analysis to save memory/space
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                print("[✓] Temp file cleaned up.")


    

        


    

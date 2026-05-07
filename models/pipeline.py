import pandas as pd 
import numpy as np
import pickle
import os

model_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(model_dir, 'model_phase1.pkl'), 'rb') as f:
    phase1_model = pickle.load(f)

with open(os.path.join(model_dir, 'model_phase2.pkl'), 'rb') as f:
    phase2_model = pickle.load(f)
class Full_pipeline():
    def __init__(self,data):
        self.Data=data
        pass
    def _nan_removal(self):
        print("Removing the Nan and duplicated values")
        self.Data.replace([np.inf, -np.inf], np.nan, inplace=True)
        self.Data.dropna(inplace=True)
        self.Data.drop_duplicates(inplace=True)
        pass
    def _feature_selected(self):
        print("Selecting the features")
        self.Data.columns=self.Data.columns.str.strip()
        
        if 'Timestamp' in self.Data.columns:
            self.Timestamps = self.Data['Timestamp'].copy()
        else:
            self.Timestamps = pd.Series(["Unknown"] * len(self.Data), index=self.Data.index)
            
        if 'IP' in self.Data.columns:
            self.IPs = self.Data['IP'].copy()
        else:
            self.IPs = pd.Series(["Unknown"] * len(self.Data), index=self.Data.index)
            
        self.Data=self.Data[['Destination Port', 'Flow Duration', 'Total Length of Fwd Packets',
       'Fwd Packet Length Mean', 'Fwd Packet Length Std',
       'Bwd Packet Length Mean', 'Bwd Packet Length Std', 'Flow Bytes/s',
       'Flow Packets/s', 'Flow IAT Std', 'Fwd IAT Total', 'Fwd IAT Mean',
       'Fwd IAT Std', 'Bwd IAT Total', 'Bwd IAT Mean', 'Bwd IAT Std',
       'Fwd PSH Flags', 'Fwd Packets/s', 'Bwd Packets/s', 'Packet Length Mean',
       'Packet Length Std', 'FIN Flag Count', 'SYN Flag Count',
       'PSH Flag Count', 'ACK Flag Count', 'URG Flag Count', 'Down/Up Ratio',
       'Avg Fwd Segment Size', 'Avg Bwd Segment Size', 'Subflow Fwd Bytes',
       'Init_Win_bytes_forward', 'Init_Win_bytes_backward', 'Active Std',
       'Idle Mean', 'Idle Std']]
        pass

    def predicting_packet_nature(self):
        if self.Data.empty:
            print("No valid data after cleaning")
            return {
                'normal_count': 0,
                'attack_count': 0,
                'attacks': []
            }, 0.0

        prediction_probability = phase1_model.predict_proba(self.Data)[:, 1]
        confidence_mean = float(np.mean(prediction_probability)) if len(prediction_probability) > 0 else 0.0
        
        predict_value = (prediction_probability >= 0.5).astype(int)
        attack_mask = predict_value == 1
        normal_count = int((predict_value == 0).sum())
        attack_count = int(attack_mask.sum())

        print(f"Normal flows: {normal_count}")
        print(f"Attack flows: {attack_count}")

        attacks = []
        if attack_count > 0:
            attacks = self.Attack(attack_mask)

        return {
            'normal_count': normal_count,
            'attack_count': attack_count,
            'attacks': attacks
        }, confidence_mean

    def Attack(self, mask):
        attack_data = self.Data[mask]
        attack_times = self.Timestamps[mask]
        attack_ips = self.IPs[mask]
        predictions = phase2_model.predict(attack_data)
        results = []
        for ip, time, pred in zip(attack_ips, attack_times, predictions):
            entry = (ip, time, str(pred))
            print(f"[{time}] IP: {ip} | Attack type: {pred}")
            results.append(entry)

        return results
    def run(self):
        self._nan_removal()
        self._feature_selected()
        return self.predicting_packet_nature()

        
        
        

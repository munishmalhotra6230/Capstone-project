import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle

from sklearn.metrics import confusion_matrix, recall_score, classification_report
# Bring the Data or add add path to retrain the model
'''
This is the module in which it used to auto retrain the model in this 
via providing or cleaning the data and just retrain it 
I can provide default features to do but some times a evaluater gets another sepcialized features which help them tp
make model more perfectly 
It can provide the metrics also to cross check again
you can add custom model instead of random forest 
'''
class retraining_pipeline_phase1():
    def __init__(self, Data):
        self.data = pd.read_csv(Data)

    def preprocess(self, features=['Destination Port', 'Flow Duration', 'Total Length of Fwd Packets',
       'Fwd Packet Length Mean', 'Fwd Packet Length Std',
       'Bwd Packet Length Mean', 'Bwd Packet Length Std', 'Flow Bytes/s',
       'Flow Packets/s', 'Flow IAT Std', 'Fwd IAT Total', 'Fwd IAT Mean',
       'Fwd IAT Std', 'Bwd IAT Total', 'Bwd IAT Mean', 'Bwd IAT Std',
       'Fwd PSH Flags', 'Fwd Packets/s', 'Bwd Packets/s', 'Packet Length Mean',
       'Packet Length Std', 'FIN Flag Count', 'SYN Flag Count',
       'PSH Flag Count', 'ACK Flag Count', 'URG Flag Count', 'Down/Up Ratio',
       'Avg Fwd Segment Size', 'Avg Bwd Segment Size', 'Subflow Fwd Bytes',
       'Init_Win_bytes_forward', 'Init_Win_bytes_backward', 'Active Std',
       'Idle Mean', 'Idle Std']):
        try:
            self.data.replace([np.inf, -np.inf], np.nan, inplace=True)
            self.data.drop_duplicates(inplace=True)
            self.data.dropna(inplace=True)
            self.X = self.data[features]
            self.y = self.data["Label"]
        except Exception as e:
            print(f"{e}")    

    def test_model_evaluation(self, model=None, threshold=0.5):
        if model is None:
            model = RandomForestClassifier(n_jobs=-1)
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, stratify=self.y, shuffle=True
        )
        self.Model = model.fit(self.X_train, self.y_train)
        ypred_prob = self.Model.predict_proba(self.X_test)[:, 1]
        ypred = (ypred_prob >= threshold).astype(int)

        print("Model Evaluation Report")
        print("------" * 20)
        print(f"Confusion Matrix:\n{confusion_matrix(self.y_test, ypred)}")
        print("------" * 20)
        print(f"Recall: {recall_score(self.y_test, ypred)}")
        print("------" * 20)
        print(f"Classification Report:\n{classification_report(self.y_test, ypred)}")
        return confusion_matrix(self.y_test, ypred),recall_score(self.y_test, ypred),classification_report(self.y_test, ypred)

    def get_pickle_file(self, name="Model"):
        with open(f"{name}{np.random.random()}_phase1.pkl", "wb") as f:
            pickle.dump(self.Model, f)
        print(f"Model saved as {name}.pkl")

    def evaluate_your_model(self, features, model=None, threshold=0.5):
        self.preprocess(features=features)
        self.test_model_evaluation(model=model, threshold=threshold)

    def retrain_model(self, features, model=None, threshold=0.5, file_name="Model"):
        self.preprocess(features=features)
        cm, rs, cr = self.test_model_evaluation(model=model, threshold=threshold)
        self.get_pickle_file(name=file_name)
        return cm, rs, cr
class retraining_phase2():
    def __init__(self, Data):
        self.data =pd.read_csv(Data)

    def preprocess(self, features=None):
        if features is None:
            raise ValueError("Features list provide karo")
        self.data.replace([np.inf, -np.inf], np.nan, inplace=True)
        self.data.drop_duplicates(inplace=True)
        self.data.dropna(inplace=True)
        self.X = self.data[features]
        self.y = self.data["Label"]

    def test_model_evaluation(self, model=None):
        if model is None:
            model = RandomForestClassifier(n_jobs=-1)
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, stratify=self.y, shuffle=True
        )
        self.Model = model.fit(self.X_train, self.y_train)
        ypred = self.Model.predict(self.X_test)

        print("Model Evaluation Report")
        print("------" * 20)
        print(f"Confusion Matrix:\n{confusion_matrix(self.y_test, ypred)}")
        print("------" * 20)
        print(f"Recall: {recall_score(self.y_test, ypred)}")
        print("------" * 20)
        print(f"Classification Report:\n{classification_report(self.y_test, ypred)}")
        return confusion_matrix(self.y_test, ypred),recall_score(self.y_test, ypred),classification_report(self.y_test, ypred)

    def get_pickle_file(self, name="Model"):
        with open(f"{name}{np.random.random()}_phase2.pkl", "wb") as f:
            pickle.dump(self.Model, f)
        print(f"Model saved as {name}.pkl")

    def evaluate_your_model(self, features, model=None):
        self.preprocess(features=features)
        self.test_model_evaluation(model=model)

    def retrain_model(self, features, model=None,  file_name="Model"):
        self.preprocess(features=features)
        cm, rs, cr = self.test_model_evaluation(model=model)
        self.get_pickle_file(name=file_name)
        return cm, rs, cr





        
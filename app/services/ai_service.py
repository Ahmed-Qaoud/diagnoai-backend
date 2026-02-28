import joblib
import pandas as pd
import json
import os
from typing import Dict, Any, List

class AIService:
    def __init__(self, model_dir: str):
        self.model_dir = model_dir
        self.feature_columns = joblib.load(os.path.join(model_dir, "cbc_feature_columns.joblib"))
        self.stage1_model = joblib.load(os.path.join(model_dir, "cbc_stage1_model.joblib"))
        self.stage2_model = joblib.load(os.path.join(model_dir, "cbc_stage2_model.joblib"))
        
        with open(os.path.join(model_dir, "medical_ontology.json"), "r") as f:
            self.ontology = json.load(f)

    def predict_cbc(self, data: Dict[str, float]) -> Dict[str, Any]:
        # Preprocessing: ensure all columns from feature_columns exist, default to 0.0
        input_df = pd.DataFrame([data])
        for col in self.feature_columns:
            if col not in input_df.columns:
                input_df[col] = 0.0
        
        # Ensure order matches feature_columns
        input_df = input_df[self.feature_columns]
        
        # Stage 1: Initial classification (e.g., Healthy vs Abnormal)
        stage1_pred = self.stage1_model.predict(input_df)[0]
        stage1_proba = self.stage1_model.predict_proba(input_df)[0].tolist()
        
        # Stage 2: Detailed diagnosis
        stage2_pred = self.stage2_model.predict(input_df)[0]
        stage2_proba = self.stage2_model.predict_proba(input_df)[0].tolist()
        
        # Mapping results to ontology
        diagnosis_key = str(stage2_pred).lower().replace(" ", "_")
        
        # Lookup in medical_ontology
        # Note: The keys in ontology are nested under "cbc_related" and "non_cbc_related"
        ontology_info = self.ontology.get("cbc_related", {}).get(diagnosis_key) or \
                        self.ontology.get("non_cbc_related", {}).get(diagnosis_key) or \
                        self.ontology.get("non_cbc_related", {}).get("general_non_cbc_related")

        return {
            "stage1_prediction": stage1_pred,
            "stage1_probability": stage1_proba,
            "stage2_prediction": stage2_pred,
            "stage2_probability": stage2_proba,
            "diagnosis": ontology_info
        }

# Singleton instance
ai_service = AIService(os.path.dirname(os.path.abspath(__file__)) + "/../..")

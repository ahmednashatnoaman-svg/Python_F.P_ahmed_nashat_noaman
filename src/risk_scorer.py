from scipy.stats import zscore
import numpy as np

class RiskScorer:
    def __init__(self):
        pass

    def calculate_risk_scores(self, features_df):
        if features_df is None: return None
        print("Scoring risks...")
        
        df = features_df.copy()
        
        # 1. Calculate Z-Scores (Simple Weighting)
        weights = {
            'max_amount': 0.3,
            'transaction_count': 0.1,
            'avg_daily_tx': 0.2,
            'max_rolling_avg_3': 0.4
        }
        
        df['risk_score_raw'] = 0.0
        
        for col, weight in weights.items():
            if col in df.columns:
                mean = df[col].mean()
                std = df[col].std()
                if std > 0:
                    z_col = (df[col] - mean) / std
                    df['risk_score_raw'] += z_col * weight

        df['risk_band'] = 'Low'
        df['risk_reason'] = 'Safe'
        
        z_score = df['risk_score_raw'].abs()
        
        if 'isFraud' in df.columns:
            mask_fraud = (df['isFraud'] == 1)
            df.loc[mask_fraud, 'risk_band'] = 'Critical'
            df.loc[mask_fraud, 'risk_reason'] = 'Known Fraud'

        mask_uncaught = (df['risk_reason'] == 'Safe')
        
        mask_crit = mask_uncaught & (z_score > 3)
        df.loc[mask_crit, 'risk_band'] = 'Critical'
        df.loc[mask_crit, 'risk_reason'] = 'Statistical Anomaly'
        
        mask_high = mask_uncaught & (z_score > 2) & (z_score <= 3)
        df.loc[mask_high, 'risk_band'] = 'High'
        df.loc[mask_high, 'risk_reason'] = 'Elevated Risk'
        
        mask_med = mask_uncaught & (z_score > 1) & (z_score <= 2)
        df.loc[mask_med, 'risk_band'] = 'Medium'
        df.loc[mask_med, 'risk_reason'] = 'Suspicious Activity'
        
        print("Scoring complete.")
        return df

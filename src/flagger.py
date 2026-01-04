import pandas as pd

class TransactionFlagger:
    def __init__(self):
        pass

    def flag_transactions(self, tx_df, risk_df):
        if tx_df is None or risk_df is None: return None
        print("Flagging suspicious transactions...")
        
        high_risk_users = risk_df[risk_df['risk_band'].isin(['Critical', 'High'])]['customer_id']
        
        flagged = tx_df[
            (tx_df['amount'] > 200000) | 
            (tx_df['customer_id'].isin(high_risk_users))
        ].copy()
        
        if 'isFraud' in tx_df.columns:
            flagged = pd.concat([flagged, tx_df[tx_df['isFraud'] == 1]])
            
        final = flagged.drop_duplicates()
        print(f"Flagged: {len(final)}")
        return final

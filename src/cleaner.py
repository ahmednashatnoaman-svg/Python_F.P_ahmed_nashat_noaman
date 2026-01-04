import pandas as pd

class TransactionCleaner:
    def __init__(self):
        pass

    def clean_data(self, df):
        if df is None: return None, None
        
        print("Cleaning data...")
        initial = len(df)
        stats = {'initial': initial}
        
        rename_map = {
            'nameOrig': 'customer_id',
            'nameDest': 'recipient_id',
            'oldbalanceOrg': 'old_balance_sender',
            'newbalanceOrig': 'new_balance_sender',
            'oldbalanceDest': 'old_balance_recipient',
            'newbalanceDest': 'new_balance_recipient',
            'step': 'time_step'
        }
        df = df.rename(columns=rename_map)

        df = df.drop_duplicates()
        
        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        if 'time_step' in df.columns:
            df['time_step'] = pd.to_numeric(df['time_step'], errors='coerce').fillna(0).astype(int)
            
        df = df.dropna(subset=['customer_id', 'amount'])
        
        if 'time_step' in df.columns:
            start = pd.Timestamp('2025-01-01')
            df['datetime'] = start + pd.to_timedelta(df['time_step'], unit='h')
            df['date'] = df['datetime'].dt.date
            df['hour'] = df['datetime'].dt.hour
            
            cutoff = pd.Timestamp('2025-01-31').date()
            df = df[df['date'] != cutoff]

        df = self.filter_illogical_data(df)
        
        cleaned = len(df)
        stats['cleaned'] = cleaned
        stats['removed'] = initial - cleaned
        
        print(f"Cleaned. Removed {stats['removed']} rows.")
        return df, stats

    def filter_illogical_data(self, df):
        print("Applying Strict Mathematical Logic...")
        
        c1_fraud = (df['isFraud'] == 1) if 'isFraud' in df.columns else False
        c2_flagged = (df['isFlaggedFraud'] == 1) if 'isFlaggedFraud' in df.columns else False
        
        valid_amt = df['amount'] != 0
        
        diff_sender_dec = abs((df['old_balance_sender'] - df['new_balance_sender']) - df['amount'])
        valid_sender_dec = diff_sender_dec < 0.01
        
        diff_rec_inc = abs((df['new_balance_recipient'] - df['old_balance_recipient']) - df['amount'])
        valid_rec_inc = diff_rec_inc < 0.01
        
        is_merchant = df['recipient_id'].str.startswith('M')
        
        valid_outgoing = valid_amt & valid_sender_dec & (valid_rec_inc | is_merchant)
        
        diff_sender_inc = abs((df['new_balance_sender'] - df['old_balance_sender']) - df['amount'])
        valid_sender_inc = diff_sender_inc < 0.01
        
        diff_rec_dec = abs((df['old_balance_recipient'] - df['new_balance_recipient']) - df['amount'])
        valid_rec_dec = diff_rec_dec < 0.01
        
        valid_incoming = valid_amt & valid_sender_inc & valid_rec_dec

        mask = c1_fraud | c2_flagged | valid_outgoing | valid_incoming
        
        return df[mask].copy()

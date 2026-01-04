import pandas as pd

class FeatureBuilder:
    def __init__(self):
        self.features = None

    def build_features(self, df):
        if df is None: return None
        if df.empty: return None

        print("Building features...")
        grouped = df.groupby('customer_id')

        features = grouped.agg(
            total_amount=('amount', 'sum'),
            avg_amount=('amount', 'mean'),
            max_amount=('amount', 'max'),
            transaction_count=('amount', 'count')
        ).reset_index()
        
        if 'isFraud' in df.columns:
            fraud = grouped['isFraud'].max().reset_index()
            features = pd.merge(features, fraud, on='customer_id', how='left')
            
        if 'isFlaggedFraud' in df.columns:
            flag = grouped['isFlaggedFraud'].max().reset_index()
            features = pd.merge(features, flag, on='customer_id', how='left')

            features = pd.merge(features, flag, on='customer_id', how='left')

        daily = df.groupby(['customer_id', 'date']).size().reset_index(name='daily_count')
        velocity = daily.groupby('customer_id')['daily_count'].agg(['mean', 'max']).reset_index()
        velocity.columns = ['customer_id', 'avg_daily_tx', 'max_daily_tx']
        features = pd.merge(features, velocity, on='customer_id', how='left').fillna(0)

        cols = ['customer_id', 'time_step', 'amount']
        df_sorted = df[cols].sort_values(['customer_id', 'time_step'])
        
        rolling = df_sorted.groupby('customer_id')['amount'].rolling(window=3, min_periods=1).mean()
        df_sorted['rolling_avg_3'] = rolling.reset_index(level=0, drop=True)
        
        max_roll = df_sorted.groupby('customer_id')['rolling_avg_3'].max().reset_index()
        max_roll.columns = ['customer_id', 'max_rolling_avg_3']
        
        features = pd.merge(features, max_roll, on='customer_id', how='left')

        self.features = features
        print(f"Features built: {len(features)}")
        return features

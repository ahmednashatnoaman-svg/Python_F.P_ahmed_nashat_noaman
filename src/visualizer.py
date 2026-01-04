import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np

class Visualizer:
    def __init__(self, output_dir="charts"):
        self.output_dir = output_dir
        sns.set_theme(style="whitegrid")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def save_plot(self, filename):
        filepath = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, bbox_inches='tight')
        plt.close()
        print(f"Saved: {filepath}")

    def plot_risk_dist(self, df):
        plt.figure(figsize=(10, 6))
        order = ['Low', 'Medium', 'High', 'Critical']
        ax = sns.countplot(data=df, x='risk_band', order=order, palette='viridis')
        plt.yscale('log')
        for p in ax.patches:
            ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='bottom', xytext=(0, 5), textcoords='offset points')
        plt.title("1. Risk Distribution (Log Scale)")
        self.save_plot("1_risk_dist.png")

    def plot_z_score(self, df):
        plt.figure(figsize=(10, 6))
        col = 'z_score' if 'z_score' in df.columns else 'risk_score_raw'
        data = df[(df[col] > -5) & (df[col] < 20)]
        sns.histplot(data=data, x=col, bins=50, kde=True, color='royalblue')
        plt.yscale('log')
        plt.axvline(x=3, color='red', linestyle='--')
        plt.title("2. Z-Score Distribution")
        self.save_plot("2_z_score.png")

    def plot_risk_ab(self, df):
        plt.figure(figsize=(10, 6))
        data = df[df['max_amount'] > 50]
        sns.boxplot(data=data, x='risk_band', y='max_amount', order=['Low', 'Medium', 'High', 'Critical'], palette='Set2')
        plt.yscale('log')
        plt.title("3. Risk vs Max Amount")
        self.save_plot("3_risk_vs_amt.png")

    def plot_fraud_map(self, df):
        if 'isFraud' not in df.columns: return
        plt.figure(figsize=(10, 6))
        pd.crosstab(df['risk_band'], df['isFraud']).reindex(['Low', 'Medium', 'High', 'Critical']).plot(kind='bar', stacked=True, color=['#3498db', '#e74c3c'], figsize=(10,6))
        plt.yscale('log')
        plt.title("4. Risk Band vs Actual Fraud")
        self.save_plot("4_fraud_map.png")

    def plot_fraud_types(self, df, tx_df):
        if tx_df is None: return
        plt.figure(figsize=(8, 8))
        crit = df[df['risk_band'].isin(['Critical', 'High'])]['customer_id']
        sub = tx_df[tx_df['customer_id'].isin(crit)]
        if sub.empty: return
        counts = sub['type'].value_counts()
        plt.pie(counts, labels=counts.index, autopct='%1.1f%%')
        plt.title("5. Critical & High Risk Transaction Types")
        self.save_plot("5_fraud_types.png")

    def plot_fraud_hourly(self, df, tx_df):
        if tx_df is None: return
        plt.figure(figsize=(12, 6))
        tx_df['hour'] = tx_df['time_step'] % 24
        crit = df[df['risk_band'] == 'Critical']['customer_id']
        norm = tx_df[~tx_df['customer_id'].isin(crit)].groupby('hour').size()
        risk = tx_df[tx_df['customer_id'].isin(crit)].groupby('hour').size()
        plt.plot(norm.index, norm.values, color='gray', alpha=0.5, label='Normal')
        ax2 = plt.gca().twinx()
        ax2.plot(risk.index, risk.values, color='red', label='Critical')
        plt.title("6. Hourly Risk Patterns")
        self.save_plot("6_fraud_hourly.png")

    def plot_type_box(self, tx_df):
        if tx_df is None: return
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=tx_df[tx_df['amount'] > 10], x='type', y='amount', palette='Set3')
        plt.yscale('log')
        plt.title("7. Amount Distribution by Type")
        self.save_plot("7_type_box.png")

    def plot_type_vol(self, tx_df):
        if tx_df is None: return
        plt.figure(figsize=(10, 6))
        sums = tx_df.groupby('type')['amount'].sum().sort_values(ascending=False)
        sums.plot(kind='bar', color=sns.color_palette("viridis", len(sums)))
        plt.title("8. Total Volume by Type")
        for i, v in enumerate(sums):
            label = f"${v/1e9:.1f}B" if v >= 1e9 else f"${v/1e6:.0f}M"
            plt.text(i, v, label, ha='center', va='bottom')
        self.save_plot("8_type_vol.png")

    def plot_daily_trend(self, tx_df):
        if tx_df is None or 'date' not in tx_df.columns: return
        plt.figure(figsize=(24, 8))
        data = tx_df.groupby(['type', 'date'])['amount'].sum().unstack(level=0).fillna(0)
        data.plot(marker='o', linewidth=2)
        plt.yscale('log')
        plt.title("9. Daily Trend by Type")
        plt.xticks(rotation=45)
        self.save_plot("9_daily_trend.png")

    def plot_hourly_curve(self, tx_df):
        if tx_df is None: return
        if 'hour' not in tx_df.columns: tx_df['hour'] = tx_df['time_step'] % 24
        plt.figure(figsize=(12, 6))
        data = tx_df.groupby('hour')['amount'].sum()
        data.plot(kind='line', color='#d35400', linewidth=3, marker='o')
        plt.fill_between(data.index, 0, data.values, color='#d35400', alpha=0.1)
        plt.title("10. Aggregate Hourly Activity")
        plt.xticks(range(24))
        self.save_plot("10_hourly_curve.png")

    def plot_hourly_ts(self, tx_df):
        if tx_df is None or 'datetime' not in tx_df.columns: return
        plt.figure(figsize=(24, 8))
        tx_df.groupby('datetime')['amount'].sum().plot(color='#e67e22', alpha=0.8)
        plt.title("11. Hourly Time Series")
        plt.xticks(rotation=45)
        self.save_plot("11_hourly_ts.png")

    def plot_daily_total(self, tx_df):
        if tx_df is None or 'date' not in tx_df.columns: return
        plt.figure(figsize=(12, 6))
        daily = tx_df.groupby('date')['amount'].sum()
        daily.plot(marker='o', color='#2c3e50')
        plt.title("12a. Daily Total Amount")
        plt.xticks(rotation=45)
        self.save_plot("12a_daily_total.png")

    def plot_daily_count(self, tx_df):
        if tx_df is None or 'date' not in tx_df.columns: return
        plt.figure(figsize=(12, 6))
        daily = tx_df.groupby('date')['amount'].count()
        daily.plot(kind='bar', color='#27ae60')
        plt.title("12b. Daily Transaction Count")
        plt.xticks(rotation=45)
        self.save_plot("12b_daily_count.png")

    def plot_daily_mean(self, tx_df):
        if tx_df is None or 'date' not in tx_df.columns: return
        plt.figure(figsize=(12, 6))
        daily = tx_df.groupby('date')['amount'].mean()
        daily.plot(marker='o', color='#e67e22')
        plt.title("12c. Daily Average Amount")
        plt.xticks(rotation=45)
        self.save_plot("12c_daily_mean.png")

    def plot_daily_max(self, tx_df):
        if tx_df is None or 'date' not in tx_df.columns: return
        plt.figure(figsize=(12, 6))
        daily = tx_df.groupby('date')['amount'].max()
        daily.plot(marker='o', color='#e74c3c')
        plt.title("12d. Daily Max Amount")
        plt.xticks(rotation=45)
        self.save_plot("12d_daily_max.png")

    def plot_risk_waterfall(self, df):
        if 'risk_reason' not in df.columns: return
        plt.figure(figsize=(12, 6))
        
        categories = ['Known Fraud', 'Statistical Anomaly']
        data = df[df['risk_reason'].isin(categories)]
        
        if data.empty: return

        counts = data['risk_reason'].value_counts().reindex(categories).fillna(0)
        colors = ['#c0392b', '#e67e22', '#f1c40f']
        
        counts.plot(kind='bar', color=colors, edgecolor='black')
        plt.title("13. Logic Breakdown (Waterfall Detection)")
        plt.ylabel("Customers Caught")
        plt.xticks(rotation=0)
        
        for i, v in enumerate(counts):
            plt.text(i, v, str(int(v)), ha='center', va='bottom', fontweight='bold')
            
        self.save_plot("13_risk_waterfall.png")

    def generate_all_plots(self, df, tx_df=None):
        print("--- Generating Visualizations ---")
        if df is None: return
        self.plot_risk_dist(df)
        self.plot_z_score(df)
        self.plot_risk_ab(df)
        self.plot_fraud_map(df)
        self.plot_fraud_types(df, tx_df)
        self.plot_fraud_hourly(df, tx_df)
        self.plot_type_box(tx_df)
        self.plot_type_vol(tx_df)
        self.plot_daily_trend(tx_df)
        self.plot_hourly_curve(tx_df)
        self.plot_hourly_ts(tx_df)
        self.plot_daily_total(tx_df)
        self.plot_daily_count(tx_df)
        self.plot_daily_mean(tx_df)
        self.plot_daily_max(tx_df)
        self.plot_risk_waterfall(df)
        print("--- Done ---")

import pandas as pd

class ReportGenerator:
    def __init__(self):
        pass

    def export_dataframe(self, df, filename):
        if df is None: return False
        try:
            df.to_csv(filename, index=False)
            print(f"Exported: {filename}")
            return True
        except Exception:
            return False

    def export_daily_stats(self, tx_df, filename="outputs/daily_stats.csv"):
        if tx_df is None or 'date' not in tx_df.columns: return False
        try:
            stats = tx_df.groupby('date')['amount'].agg(['count', 'sum', 'mean', 'max']).reset_index()
            stats.columns = ['Date', 'Count', 'Total', 'Avg', 'Max']
            stats.sort_values('Date').to_csv(filename, index=False)
            print(f"Exported: {filename}")
            return True
        except Exception:
            return False

    def generate_summary_report(self, risk_df, flagged_df, tx_df=None, filename="report.txt"):
        print(f"Generating report: {filename}")
        json_data = {}
        try:
            with open(filename, 'w') as f:
                f.write("Bank Transaction Risk & Anomaly Analyzer - Summary Report\n")
                f.write("=========================================================\n\n")
                
                if tx_df is not None:
                    f.write("Payment Type Statistics:\n")
                    f.write("------------------------\n")
                    f.write(f"{'Type':<15} {'Count':>10} {'Mean':>15} {'Max':>15} {'Sum':>20}\n")
                    f.write("-" * 75 + "\n")
                    
                    type_stats = tx_df.groupby('type')['amount'].agg(['count', 'mean', 'max', 'sum'])
                    
                    json_data['payment_types'] = []
                    
                    for type_name, row in type_stats.iterrows():
                        f.write(f"{type_name:<15} {int(row['count']):>10,d} {row['mean']:>15,.2f} {row['max']:>15,.2f} {row['sum']:>20,.2f}\n")
                        json_data['payment_types'].append({
                            'type': type_name,
                            'count': int(row['count']),
                            'mean': float(row['mean']),
                            'max': float(row['max']),
                            'sum': float(row['sum'])
                        })
                    f.write("\n")

                    if 'date' in tx_df.columns:
                        f.write("Daily Customer Statistics (Grouped by Customer & Date):\n")
                        f.write("------------------------------------------------------\n")
                        daily_cust = tx_df.groupby(['customer_id', 'date'])['amount'].sum()
                        f.write(f"Average Daily Amount per Customer: {daily_cust.mean():,.2f}\n")
                        f.write(f"Median Daily Amount per Customer:  {daily_cust.median():,.2f}\n")
                        f.write(f"Max Daily Amount (Single Cust):    {daily_cust.max():,.2f}\n\n")
                        
                        json_data['daily_stats'] = {
                            'avg_daily_per_cust': float(daily_cust.mean()),
                            'median_daily_per_cust': float(daily_cust.median()),
                            'max_daily_single': float(daily_cust.max())
                        }

                    if 'time_step' in tx_df.columns:
                        tx_df['hour'] = tx_df['time_step'] % 24
                        hourly = tx_df.groupby('hour')['amount'].agg(['mean', 'max', 'sum'])
                        
                        f.write("Hourly Statistics (Aggregated by Hour 0-23):\n")
                        f.write("--------------------------------------------\n")
                        f.write(f"{'Hour':<10} {'Mean Amount':>15} {'Max Amount':>15} {'Total Sum':>20}\n")
                        f.write("-" * 60 + "\n")
                        
                        json_data['hourly_stats'] = []
                        for hour, row in hourly.iterrows():
                            f.write(f"{hour:<10} {row['mean']:>15,.2f} {row['max']:>15,.2f} {row['sum']:>20,.2f}\n")
                            json_data['hourly_stats'].append({
                                'hour': int(hour),
                                'mean': float(row['mean']),
                                'max': float(row['max']),
                                'sum': float(row['sum'])
                            })
                        f.write("\n")

                if risk_df is not None:
                    f.write("Customer Risk Summary:\n")
                    f.write(f"Total Customers Scored: {len(risk_df)}\n")
                    counts = risk_df['risk_band'].value_counts()
                    
                    json_data['risk_summary'] = {
                        'total_scored': len(risk_df),
                        'bands': {}
                    }
                    
                    for band in ['Low', 'Medium', 'High', 'Critical']: 
                        count = counts.get(band, 0)
                        f.write(f"  - {band}: {count}\n")
                        json_data['risk_summary']['bands'][band] = int(count)
                    f.write("\n")
                    
                    f.write("Top 5 High Risk Customers:\n")
                    crit = risk_df.sort_values('risk_score_raw', ascending=False).head(5)
                    
                    json_data['top_risky_customers'] = []
                    for _, row in crit.iterrows():
                        f.write(f"  - Customer: {row['customer_id']}, Risk Score: {row['risk_score_raw']:.2f}, Band: {row['risk_band']}\n")
                        json_data['top_risky_customers'].append({
                            'customer_id': row['customer_id'],
                            'risk_score': float(row['risk_score_raw']),
                            'risk_band': row['risk_band']
                        })
                    f.write("\n")

                if flagged_df is not None:
                    f.write("Suspicious Transactions Summary:\n")
                    f.write(f"Total Flagged Transactions: {len(flagged_df)}\n")
                    avg_flagged = 0
                    if not flagged_df.empty:
                        avg_flagged = flagged_df['amount'].mean()
                        f.write(f"Average Amount of Flagged Transactions: {avg_flagged:,.2f}\n")
                    f.write("\n")
                    
                    json_data['flagged_summary'] = {
                        'total_flagged': len(flagged_df),
                        'avg_flagged_amount': float(avg_flagged)
                    }
            # Save as JS for Dashboard (Bypasses CORS)
            import json
            js_path = "extramile_Ui/dashboard_data.js"
            try:
                with open(js_path, 'w') as jf:
                    json_str = json.dumps(json_data, indent=4)
                    jf.write(f"const DASHBOARD_DATA = {json_str};")
                print(f"Dashboard Data exported: {js_path}")
            except Exception as e:
                print(f"Error saving dashboard data: {e}")
                
            print("Report generated.")
            return True
        except Exception as e:
            print(f"Error: {e}")

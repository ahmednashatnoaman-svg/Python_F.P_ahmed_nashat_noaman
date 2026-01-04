import sys
import os
from src.data_manager import DataManager
from src.cleaner import TransactionCleaner
from src.features import FeatureBuilder
from src.risk_scorer import RiskScorer
from src.flagger import TransactionFlagger
from src.reporter import ReportGenerator
from src.visualizer import Visualizer

class ConsoleApp:
    def __init__(self):
        self.data_manager = DataManager()
        self.cleaner = TransactionCleaner()
        self.feature_builder = FeatureBuilder()
        self.risk_scorer = RiskScorer()
        self.flagger = TransactionFlagger()
        self.reporter = ReportGenerator()
        self.visualizer = Visualizer()
        
        self.df = None
        self.features = None
        self.scored_customers = None
        self.flagged_transactions = None

    def run(self):
        while True:
            print("\n--- Bank Transaction Risk Analyzer ---")
            print("1. Load Data")
            print("2. Clean Data")
            print("3. Build Features")
            print("4. Score Customers")
            print("5. Flag Transactions")
            print("6. Export Reports")
            print("7. Show Summary")
            print("8. Visualize")
            print("0. Exit")
            
            choice = input("Choice: ")
            
            if choice == '1':
                path = input("Path (data/transactions.csv): ") or "data/transactions.csv"
                self.df = self.data_manager.load_data(path)
                
            elif choice == '2':
                if self.df is None:
                    print("Please load data first (Option 1).")
                else:
                    self.df, stats = self.cleaner.clean_data(self.df)
                    if stats:
                        self.data_manager.save_data(self.df, "data/cleaned_transactions.csv")
                    
            elif choice == '3':
                if self.df is None:
                    print("Please load data first (Option 1).")
                elif 'customer_id' not in self.df.columns:
                    print("Please clean data first (Option 2) to generate 'customer_id'.")
                else:
                    self.features = self.feature_builder.build_features(self.df)
                
            elif choice == '4':
                if self.features is None:
                    print("Please build features first (Option 3).")
                else:
                    self.scored_customers = self.risk_scorer.calculate_risk_scores(self.features)
                
            elif choice == '5':
                if self.df is None:
                     print("Please load/clean data first.")
                elif self.scored_customers is None:
                     print("Please score customers first (Option 4).")
                else:
                    self.flagged_transactions = self.flagger.flag_transactions(self.df, self.scored_customers)
                
            elif choice == '6':
                if self.scored_customers is None:
                    print("No risk scores to export. Please run Option 4.")
                else:
                    if self.scored_customers is not None:
                        self.reporter.export_dataframe(self.scored_customers, "outputs/customer_risk_summary.csv")
                    if self.flagged_transactions is not None:
                        self.reporter.export_dataframe(self.flagged_transactions, "outputs/flagged_transactions.csv")
                    if self.df is not None:
                        self.reporter.export_daily_stats(self.df, "outputs/daily_stats.csv")
                    
                    self.reporter.generate_summary_report(self.scored_customers, self.flagged_transactions, self.df, filename="outputs/report.txt")
 
            elif choice == '7':
                if self.df is not None:
                    print("\n" + "="*40)
                    print("       EXECUTIVE DATA SUMMARY")
                    print("="*40)
                    
                    print(f"\n[1] FINANCIAL OVERVIEW")
                    print(f"    Total Transactions: {len(self.df):,}")
                    print(f"    Total Volume Moved: ${self.df['amount'].sum():,.2f}")
                    print(f"    Max Transaction:    ${self.df['amount'].max():,.2f}")
                    print(f"    Avg Transaction:    ${self.df['amount'].mean():,.2f}")
                    
                    if 'date' in self.df.columns:
                        print(f"    Timeline:           {self.df['date'].min()} to {self.df['date'].max()}")
                    
                    col = 'transaction_type' if 'transaction_type' in self.df.columns else 'type'
                    if col in self.df.columns:
                        print(f"\n[2] TRANSACTION TYPES")
                        counts = self.df[col].value_counts()
                        for type_name, count in counts.items():
                            print(f"    - {type_name:<15} {count:,}")

                    if self.scored_customers is not None:
                        print(f"\n[3] RISK INTELLIGENCE")
                        print("    Customers by Risk Band:")
                        bands = self.scored_customers['risk_band'].value_counts()
                        for band in ['Critical', 'High', 'Medium', 'Low']:
                            val = bands.get(band, 0)
                            print(f"    - {band:<10} {val:,}")
                    else:
                        print("\n[!] Risk Analysis not run yet (Select Option 4).")
                        
                    print("="*40 + "\n")
                else:
                    print("No data loaded.")
 
            elif choice == '8':
                if self.scored_customers is None or self.df is None:
                    print("Please run the full pipeline (Load -> Clean -> Features -> Score) before visualizing.")
                else:
                    self.visualizer.generate_all_plots(self.scored_customers, self.df)

            elif choice == '0':
                print("Bye.")
                break

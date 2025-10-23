# utils/preprocess.py
import pandas as pd

def load_csv(file_path):
    """Load bank statement CSV file"""
    try:
        df = pd.read_csv(file_path)
        print(f"✅ Loaded file: {file_path} ({len(df)} rows)")
        return df
    except Exception as e:
        print("❌ Error loading CSV:", e)
        return pd.DataFrame()

def clean_transactions(df):
    """Clean and normalize transaction data"""
    df = df.copy()
    
    # Standardize column names
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    
    # Keep necessary columns only
    expected_cols = ['date', 'description', 'amount', 'type']
    df = df[[col for col in df.columns if col in expected_cols]]
    
    # Convert dates and amounts
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    
    # Drop missing or invalid rows
    df.dropna(subset=['date', 'amount'], inplace=True)
    df.drop_duplicates(inplace=True)
    
    # Normalize description text
    df['description'] = df['description'].astype(str).str.lower()
    df['description'] = df['description'].str.replace('[^a-zA-Z0-9 ]', '', regex=True)
    
    print("✅ Cleaning completed.")
    return df

def save_cleaned_data(df, output_path):
    """Save cleaned data to CSV"""
    df.to_csv(output_path, index=False)
    print(f"📁 Cleaned data saved to: {output_path}")

# Example run (uncomment if running standalone)
# if __name__ == "__main__":
#     df_raw = load_csv("data/sample_statements.csv")
#     df_clean = clean_transactions(df_raw)
#     save_cleaned_data(df_clean, "data/cleaned_statements.csv")

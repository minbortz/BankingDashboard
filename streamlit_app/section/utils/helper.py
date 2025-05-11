import pandas as pd
from sqlalchemy import create_engine, text
from typing import Optional

# Configure MySQL connection
DB_USER = 'root'
DB_PASS = 'C0conutm!lkshak3'
DB_HOST = 'localhost:3306'
DB_NAME1 = 'Database_1'
DB_NAME2 = 'Database_2'

# SQLAlchemy Engine
engine1 = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME1}')

def save_dataframe_to_db(df: pd.DataFrame, table_name: str):
    try:
        # Convert table name to lowercase, safe format
        safe_table_name = table_name.lower().replace(" ", "_")
        df.to_sql(safe_table_name, con=engine1, if_exists='replace', index=False)
        return True, f"Data saved to `{safe_table_name}` successfully."
    except Exception as e:
        return False, str(e)
    
def search_database(query: str) -> Optional[pd.DataFrame]:
    try:
        with engine1.connect() as conn:
            result = conn.execute(text(query))
            if result.returns_rows:
                return pd.DataFrame(result.fetchall(), columns=result.keys())
            else:
                return None
    except Exception as e:
        raise e  # Re-raise the exception to be handled by the caller
    
engine2 = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME2}')

def insert_user(user_id, username, password, email, timestamp, role):
    query = text("""
        INSERT INTO user_information (userID, username, password, email, signup_time, role)
        VALUES (:userID, :username, :password, :email, :signup_time, :role)
    """)
    with engine2.connect() as conn:
        conn.execute(query, {
            "userID": user_id,
            "username": username,
            "password": password,
            "email": email,
            "signup_time": timestamp,
            "role": role
        })
        conn.commit()

def insert_admin(user_id, username, password, email, timestamp, role):
    query = text("""
        INSERT INTO admin_information (userID, username, password, email, signup_time, role)
        VALUES (:userID, :username, :password, :email, :signup_time, :role)
    """)
    with engine2.connect() as conn:
        conn.execute(query, {
            "userID": user_id,
            "username": username,
            "password": password,
            "email": email,
            "signup_time": timestamp,
            "role": role
        })
        conn.commit()


def get_user_by_username(username):
    query = text("SELECT * FROM user_information WHERE username = :username")
    with engine2.connect() as conn:
        result = conn.execute(query, {"username": username}).fetchone()
        if result:
            return result._mapping
        return None

def get_admin_by_username(username):
    query = text("SELECT * FROM admin_information WHERE username = :username")
    with engine2.connect() as conn:
        result = conn.execute(query, {"username": username}).fetchone()
        if result:
            return result._mapping
        return None
    
CRITICAL_KEYWORDS = [
    # Account/Customer Basics
    "account", "account_number", "account_id", "customer", "customer_id", "client", "user_id",
    "name", "full_name", "email", "phone", "address", "dob", "gender", "national_id",
    
    # Transactions
    "transaction", "transaction_id", "transaction_type", "date", "timestamp", "amount", "currency",
    "status", "reference", "channel", "mode", "description", "remarks",

    # Account Balances & Limits
    "balance", "available_balance", "current_balance", "limit", "overdraft", "credit_limit",

    # Loans & Credit
    "loan", "loan_id", "loan_type", "loan_amount", "interest_rate", "term", "repayment", "emi",
    "installment", "principal", "maturity_date", "collateral", "default", "credit_score",

    # Cards & Payments
    "card", "card_number", "debit", "credit", "payment", "payment_method", "payment_status",

    # Deposits & Withdrawals
    "deposit", "withdrawal", "cash", "cheque", "transfer",

    # Risk & Compliance
    "risk", "fraud", "flag", "sanction", "blacklist", "kyc", "aml", "compliance",

    # Other Useful Fields
    "branch", "ifsc", "swift", "bank_code", "institution", "region", "country", "currency_code",
    "exchange_rate", "fee", "charge", "tax", "vat", "penalty", "commission"
]


def identify_critical_columns(df_columns, keywords=CRITICAL_KEYWORDS):
    """Identifies potential critical columns based on keywords."""
    critical_cols = set()
    for col in df_columns:
        lower_col = col.lower()
        for keyword in keywords:
            if keyword in lower_col:
                critical_cols.add(col)
                break  # Move to the next column once a keyword is found
    return list(critical_cols)

def highlight_critical_and_edited(df, original_df, critical_columns):
    """Highlights only edited cells. Edited critical columns are shown in red + larger font."""
    styles = pd.DataFrame("", index=df.index, columns=df.columns)

    for col in df.columns:
        if col not in original_df.columns:
            continue  # skip if column not in original (to avoid errors)

        for i in df.index:
            if i not in original_df.index:
                continue  # skip rows that don't exist in the original

            val_df = df.at[i, col]
            val_orig = original_df.at[i, col]

            edited = False
            if pd.isnull(val_df) and pd.isnull(val_orig):
                continue
            elif str(val_df) != str(val_orig):
                edited = True

            if edited:
                if col in critical_columns:
                    styles.at[i, col] = 'background-color: #ffeeba; color: red; font-size: 120%;'
                else:
                    styles.at[i, col] = 'background-color: #ffeeba; color: black;'

    return styles

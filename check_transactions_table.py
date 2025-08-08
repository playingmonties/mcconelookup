import psycopg2
import pandas as pd

# PostgreSQL connection string
DATABASE_URL = "postgresql://postgres.hwfrwtuqpjbkuywgcvwn:Enoccm_1199@aws-0-ap-south-1.pooler.supabase.com:5432/postgres"

try:
    # Connect to the database
    print("🔌 Connecting to PostgreSQL database...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("✅ Successfully connected to database!")
    
    # Examine the transactions table
    print("\n🔍 Examining transactions table:")
    
    # Get column information
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'transactions'
        ORDER BY ordinal_position;
    """)
    
    columns = cursor.fetchall()
    print(f"Columns in transactions table:")
    for col in columns:
        print(f"  📝 {col[0]} ({col[1]}) - Nullable: {col[2]}")
    
    # Get row count
    cursor.execute("SELECT COUNT(*) FROM transactions")
    count = cursor.fetchone()[0]
    print(f"\nTotal rows: {count}")
    
    # Get sample data
    if count > 0:
        cursor.execute("SELECT * FROM transactions LIMIT 5")
        sample_data = cursor.fetchall()
        print(f"\n📊 Sample data (first 5 rows):")
        for i, row in enumerate(sample_data, 1):
            print(f"  Row {i}: {row}")
    
    cursor.close()
    conn.close()
    print("\n✅ Database connection closed")
    
except Exception as e:
    print(f"❌ Error connecting to database: {e}")

import os
import psycopg2

# Get database URL from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres.hwfrwtuqpjbkuywgcvwn:Enoccm_1199@aws-0-ap-south-1.pooler.supabase.com:5432/postgres')

print(f"Testing database connection...")
print(f"Database URL: {DATABASE_URL[:50]}...")

try:
    # Connect to the database
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("✅ Successfully connected to database!")
    
    # Test a simple query
    cursor.execute("SELECT COUNT(*) FROM transactions")
    count = cursor.fetchone()[0]
    print(f"✅ Found {count} transactions in database")
    
    # Test property search
    cursor.execute("SELECT DISTINCT property FROM transactions LIMIT 5")
    properties = cursor.fetchall()
    print(f"✅ Sample properties: {[p[0] for p in properties]}")
    
    cursor.close()
    conn.close()
    print("✅ Database connection test completed successfully")
    
except Exception as e:
    print(f"❌ Error connecting to database: {e}")
    print(f"Error type: {type(e).__name__}")

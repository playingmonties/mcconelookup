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
    
    # List all tables in the public schema
    print("\n📋 Listing all tables in public schema:")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    tables = cursor.fetchall()
    if tables:
        print(f"Found {len(tables)} tables:")
        for table in tables:
            print(f"  📊 {table[0]}")
    else:
        print("No tables found in public schema")
    
    # List all schemas
    print("\n📁 Listing all schemas:")
    cursor.execute("""
        SELECT schema_name 
        FROM information_schema.schemata
        ORDER BY schema_name;
    """)
    
    schemas = cursor.fetchall()
    print(f"Found {len(schemas)} schemas:")
    for schema in schemas:
        print(f"  📁 {schema[0]}")
    
    # If we found any tables, let's examine the first one
    if tables:
        first_table = tables[0][0]
        print(f"\n🔍 Examining table: {first_table}")
        
        # Get column information
        cursor.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = '{first_table}'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print(f"Columns in {first_table}:")
        for col in columns:
            print(f"  📝 {col[0]} ({col[1]}) - Nullable: {col[2]}")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {first_table}")
        count = cursor.fetchone()[0]
        print(f"Total rows: {count}")
        
        # Get sample data
        if count > 0:
            cursor.execute(f"SELECT * FROM {first_table} LIMIT 3")
            sample_data = cursor.fetchall()
            print(f"\n📊 Sample data (first 3 rows):")
            for i, row in enumerate(sample_data, 1):
                print(f"  Row {i}: {row}")
    
    cursor.close()
    conn.close()
    print("\n✅ Database connection closed")
    
except Exception as e:
    print(f"❌ Error connecting to database: {e}")

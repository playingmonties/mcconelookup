import psycopg2

# PostgreSQL connection string
DATABASE_URL = "postgresql://postgres.hwfrwtuqpjbkuywgcvwn:Enoccm_1199@aws-0-ap-south-1.pooler.supabase.com:5432/postgres"

try:
    # Connect to the database
    print("🔌 Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("✅ Successfully connected to database!")
    
    # Check total count
    cursor.execute("SELECT COUNT(*) FROM transactions")
    total_count = cursor.fetchone()[0]
    print(f"📊 Total transactions: {total_count}")
    
    # Get some sample properties
    cursor.execute("""
        SELECT DISTINCT property 
        FROM transactions 
        WHERE property IS NOT NULL AND property != ''
        ORDER BY property
        LIMIT 20
    """)
    
    properties = cursor.fetchall()
    print(f"\n📋 Sample properties in database:")
    for i, prop in enumerate(properties, 1):
        print(f"  {i}. {prop[0]}")
    
    # Test search for "collective"
    print(f"\n🔍 Testing search for 'collective':")
    cursor.execute("""
        SELECT DISTINCT property 
        FROM transactions 
        WHERE property ILIKE '%collective%'
        ORDER BY property
    """)
    
    collective_results = cursor.fetchall()
    if collective_results:
        print(f"✅ Found {len(collective_results)} properties containing 'collective':")
        for prop in collective_results:
            print(f"  - {prop[0]}")
    else:
        print("❌ No properties found containing 'collective'")
    
    # Test search for "greens"
    print(f"\n🔍 Testing search for 'greens':")
    cursor.execute("""
        SELECT DISTINCT property 
        FROM transactions 
        WHERE property ILIKE '%greens%'
        ORDER BY property
    """)
    
    greens_results = cursor.fetchall()
    if greens_results:
        print(f"✅ Found {len(greens_results)} properties containing 'greens':")
        for prop in greens_results:
            print(f"  - {prop[0]}")
    else:
        print("❌ No properties found containing 'greens'")
    
    cursor.close()
    conn.close()
    print("\n✅ Database connection closed")
    
except Exception as e:
    print(f"❌ Error: {e}")

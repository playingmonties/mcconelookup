import pandas as pd
import os
import glob
import requests
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://yqnhpnpdvughdkdnlcrv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlxbmhwbnBkdnVnaGRrZG5sY3J2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ2NTY0MDQsImV4cCI6MjA3MDIzMjQwNH0.g0oN1YrrtmaXGrS67VtMQG8DpA1TGXDydpaMb3D1UNk"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_database_table():
    """Create the dubai_transactions table in Supabase"""
    print("Creating database table...")
    
    # SQL to create the table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS dubai_transactions (
        id BIGSERIAL PRIMARY KEY,
        community TEXT,
        property TEXT,
        unit TEXT,
        transaction_date DATE,
        price_aed NUMERIC,
        price_per_sqft NUMERIC,
        developer TEXT,
        property_type TEXT,
        bedrooms TEXT,
        built_up_area_sqft NUMERIC,
        owner_name TEXT,
        owner_mobile_1 TEXT,
        owner_mobile_2 TEXT,
        original_mobile TEXT,
        owner_country TEXT,
        transaction_type TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Create indexes for fast searching
    CREATE INDEX IF NOT EXISTS idx_property ON dubai_transactions(property);
    CREATE INDEX IF NOT EXISTS idx_unit ON dubai_transactions(unit);
    CREATE INDEX IF NOT EXISTS idx_community ON dubai_transactions(community);
    CREATE INDEX IF NOT EXISTS idx_property_unit ON dubai_transactions(property, unit);
    """
    
    try:
        # Execute the SQL
        result = supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
        print("✅ Database table created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False

def migrate_excel_files():
    """Migrate all Excel files to the database"""
    print("Starting Excel to Database migration...")
    
    # Find all Excel files
    excel_files = glob.glob("*.xlsx")
    # Filter out temporary files
    excel_files = [f for f in excel_files if not f.startswith("~$")]
    
    print(f"Found {len(excel_files)} Excel files to migrate")
    
    total_records = 0
    
    for file_path in excel_files:
        try:
            filename = os.path.basename(file_path)
            community = filename.replace("_preprocessing.xlsx", "").replace("_", " ").title()
            
            print(f"Processing {filename}...")
            
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Clean and prepare data
            df = df.dropna(subset=['property', 'Unit'])
            df['property'] = df['property'].astype(str).str.strip()
            df['Unit'] = df['Unit'].astype(str).str.strip()
            df['community'] = community
            
            # Rename columns to match database
            df = df.rename(columns={
                'Unit': 'unit',
                'price aed': 'price_aed',
                'owner_mobile_1': 'owner_mobile_1',
                'owner_mobile_2': 'owner_mobile_2',
                'original_mobile': 'original_mobile',
                'owner_country': 'owner_country',
                'transaction_type': 'transaction_type'
            })
            
            # Select only the columns we need
            columns_to_keep = [
                'community', 'property', 'unit', 'transaction_date', 'price_aed',
                'price_per_sqft', 'developer', 'property_type', 'bedrooms',
                'built_up_area_sqft', 'owner_name', 'owner_mobile_1',
                'owner_mobile_2', 'original_mobile', 'owner_country', 'transaction_type'
            ]
            
            # Keep only columns that exist
            existing_columns = [col for col in columns_to_keep if col in df.columns]
            df = df[existing_columns]
            
            # Convert to records for insertion
            records = df.to_dict('records')
            
            # Insert into database
            if records:
                result = supabase.table('dubai_transactions').insert(records).execute()
                inserted_count = len(records)
                total_records += inserted_count
                print(f"✅ Inserted {inserted_count} records from {filename}")
            else:
                print(f"⚠️ No valid records found in {filename}")
                
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            continue
    
    print(f"\n🎉 Migration complete! Total records inserted: {total_records}")
    return total_records

def test_database():
    """Test the database connection and queries"""
    print("\nTesting database...")
    
    try:
        # Test property search
        properties = supabase.table('dubai_transactions').select('property').limit(5).execute()
        print(f"✅ Database connection working. Sample properties: {len(properties.data)} records")
        
        # Test count
        count_result = supabase.table('dubai_transactions').select('id', count='exact').execute()
        total_count = count_result.count
        print(f"✅ Total records in database: {total_count}")
        
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Supabase Database Migration")
    print("=" * 50)
    
    # Step 1: Create table
    if create_database_table():
        # Step 2: Migrate data
        total_records = migrate_excel_files()
        
        # Step 3: Test database
        if test_database():
            print("\n🎉 Migration successful!")
            print(f"📊 Total records migrated: {total_records}")
            print("🌐 Your data is now ready for the web app!")
        else:
            print("\n❌ Migration completed but database test failed")
    else:
        print("\n❌ Migration failed - could not create database table")


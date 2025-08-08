import os
import glob
import requests

# Supabase configuration
SUPABASE_URL = "https://yqnhpnpdvughdkdnlcrv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlxbmhwbnBkdnVnaGRrZG5sY3J2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ2NTY0MDQsImV4cCI6MjA3MDIzMjQwNH0.g0oN1YrrtmaXGrS67VtMQG8DpA1TGXDydpaMb3D1UNk"

def upload_excel_files():
    """Upload all Excel files to Supabase Storage using REST API"""
    
    # Find all Excel files, excluding temporary files
    excel_files = glob.glob("*.xlsx")
    # Filter out temporary files (those starting with ~$)
    excel_files = [f for f in excel_files if not f.startswith("~$")]
    
    print(f"Found {len(excel_files)} Excel files to upload")
    
    uploaded_count = 0
    for file_path in excel_files:
        try:
            filename = os.path.basename(file_path)
            print(f"Uploading {filename}...")
            
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Upload using REST API
            upload_url = f"{SUPABASE_URL}/storage/v1/object/excel-files/{filename}"
            
            upload_headers = {
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            }
            
            response = requests.post(
                upload_url,
                data=file_content,
                headers=upload_headers
            )
            
            if response.status_code == 200:
                uploaded_count += 1
                print(f"✅ Successfully uploaded {filename}")
            else:
                print(f"❌ Error uploading {filename}: {response.status_code} - {response.text}")
            
        except Exception as e:
            print(f"❌ Error uploading {filename}: {e}")
            continue
    
    print(f"\n🎉 Upload complete! {uploaded_count} files uploaded to Supabase Storage")

if __name__ == "__main__":
    upload_excel_files()

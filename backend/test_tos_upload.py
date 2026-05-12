#!/usr/bin/env python3
"""
Test script to upload README.md to BytePlus TOS using TOS service.
"""

import os
import sys
import requests
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.tos_service import get_tos_service
from utils.file_utils import save_link_to_txt


def upload_file_to_tos(file_path: str):
    """
    Upload a file to TOS using pre-signed URL.
    
    Args:
        file_path: Path to file to upload
    """
    print("=" * 60)
    print("TOS Upload Test")
    print("=" * 60)
    
    # Check if file exists
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"❌ Error: File not found: {file_path}")
        return False
    
    file_size = file_path.stat().st_size
    filename = file_path.name
    content_type = "text/markdown" if filename.endswith(".md") else "application/octet-stream"
    
    print(f"\n📄 File: {filename}")
    print(f"📏 Size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
    print(f"🔧 Content-Type: {content_type}")
    
    try:
        # Step 1: Initialize TOS service
        print("\n[1/5] Initializing TOS service...")
        tos_service = get_tos_service()
        print("✅ TOS service initialized")
        print(f"   Bucket: {tos_service.bucket}")
        print(f"   Region: {tos_service.region}")
        
        # Step 2: Generate pre-signed URL
        print("\n[2/5] Generating pre-signed PUT URL...")
        presigned_result = tos_service.generate_presigned_url(
            filename=filename,
            content_type=content_type,
            size=file_size,
        )
        print("✅ Pre-signed URL generated")
        print(f"   Key: {presigned_result['key']}")
        print(f"   Expires: {presigned_result['expiresAt']}")
        
        # Step 3: Upload file using pre-signed URL
        print("\n[3/5] Uploading file to TOS...")
        with open(file_path, 'rb') as f:
            response = requests.put(
                presigned_result['uploadUrl'],
                data=f,
                headers={'Content-Type': content_type}
            )
        
        if response.status_code >= 200 and response.status_code < 300:
            print("✅ File uploaded successfully")
            print(f"   Status: {response.status_code}")
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # Step 4: Generate signed GET URL
        print("\n[4/5] Generating signed GET URL...")
        signed_url = tos_service.generate_signed_url(presigned_result['key'])
        print("✅ Signed URL generated")
        print(f"   Signed URL: {signed_url[:80]}...")
        
        # Step 5: Save link to txt file
        print("\n[5/5] Saving link to txt file...")
        txt_path = save_link_to_txt(filename, presigned_result['publicUrl'])
        print("✅ Link saved to txt file")
        print(f"   Path: {txt_path}")
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ Upload Test Successful!")
        print("=" * 60)
        print(f"\n📁 File Key: {presigned_result['key']}")
        print(f"🔗 Public URL: {presigned_result['publicUrl']}")
        print(f"🔐 Signed URL: {signed_url}")
        print(f"📄 TXT File: {txt_path}")
        print(f"\n⏰ Expires At: {presigned_result['expiresAt']}")
        
        # Verify signed URL works
        print("\n🔍 Verifying signed URL...")
        verify_response = requests.get(signed_url)
        if verify_response.status_code == 200:
            print("✅ Signed URL is accessible")
            print(f"   Content length: {len(verify_response.text)} bytes")
        else:
            print(f"⚠️  Signed URL returned status {verify_response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check if file path is provided
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Default to README.md in parent directory
        file_path = "../README.md"
    
    print(f"\n🚀 Starting TOS upload test...")
    print(f"📂 Target file: {file_path}\n")
    
    success = upload_file_to_tos(file_path)
    
    if success:
        print("\n🎉 Test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
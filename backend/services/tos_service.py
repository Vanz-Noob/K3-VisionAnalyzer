import os
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

try:
    from tos import TosClientV2, HttpMethodType
except ImportError:
    raise ImportError(
        "tos-python-sdk is not installed. "
        "Install it with: pip install tos-python-sdk"
    )


class TOSService:
    """BytePlus TOS Service for managing object storage operations."""
    
    def __init__(self):
        """Initialize TOS client with environment variables."""
        self.access_key_id = os.environ.get("TOS_ACCESS_KEY_ID")
        self.secret_access_key = os.environ.get("TOS_SECRET_ACCESS_KEY")
        self.region = os.environ.get("TOS_REGION", "ap-southeast-1")
        self.bucket = os.environ.get("TOS_BUCKET")
        self.endpoint = os.environ.get("TOS_ENDPOINT")
        
        if not all([self.access_key_id, self.secret_access_key, self.bucket]):
            raise ValueError(
                "Missing required TOS environment variables: "
                "TOS_ACCESS_KEY_ID, TOS_SECRET_ACCESS_KEY, TOS_BUCKET"
            )
        
        # Initialize TOS client
        # Ensure endpoint has protocol
        endpoint_url = self.endpoint
        if endpoint_url and not endpoint_url.startswith(('http://', 'https://')):
            endpoint_url = f"https://{endpoint_url}"
            
        self.client = TosClientV2(
             self.access_key_id,
             self.secret_access_key,
             endpoint_url,
             self.region,
         )
    
    def upload_file(
        self,
        file_path: str,
        object_name: str = None
    ) -> Dict[str, Any]:
        """
        Upload a file directly from server to TOS.
        Equivalent to the old put_object implementation but using the official SDK.
        
        Args:
            file_path: Local path to the file
            object_name: Optional key for the object. If not provided, filename will be used.
            
        Returns:
            Dictionary containing publicUrl, key, and success status
        """
        if not object_name:
            object_name = f"uploads/{os.path.basename(file_path)}"
            
        # Ensure object name doesn't start with slash
        if object_name.startswith('/'):
            object_name = object_name.lstrip('/')
            
        try:
            # Upload using the SDK
            with open(file_path, 'rb') as f:
                self.client.put_object(self.bucket, object_name, content=f)
            
            # Construct public URL
            public_url = self._construct_public_url(object_name)
            
            return {
                "success": True,
                "publicUrl": public_url,
                "key": object_name
            }
        except Exception as e:
            # If it fails, try with a more explicit error message
            logger.error(f"TOS SDK Upload Error: {str(e)}")
            raise Exception(f"Failed to upload file to TOS: {str(e)}")

    def get_object(self, key: str, local_path: str) -> bool:
        """
        Download an object from TOS to a local file.
        
        Args:
            key: Object key in the bucket
            local_path: Local path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure local directory exists
            os.makedirs(os.path.dirname(os.path.abspath(local_path)), exist_ok=True)
            
            # Download using the SDK
            result = self.client.get_object(self.bucket, key)
            with open(local_path, 'wb') as f:
                # The result.read() returns a stream
                f.write(result.read())
            
            return True
        except Exception as e:
            logger.error(f"Failed to download object {key}: {str(e)}")
            return False

    def list_objects(self, prefix: str = "", max_keys: int = 1000) -> list:
        """
        List objects in the bucket with an optional prefix.
        
        Args:
            prefix: Prefix to filter objects
            max_keys: Maximum number of keys to return
            
        Returns:
            List of object metadata
        """
        try:
            result = self.client.list_objects(
                self.bucket,
                prefix=prefix,
                max_keys=max_keys
            )
            
            objects = []
            if result.contents:
                for obj in result.contents:
                    objects.append({
                        'name': obj.key,
                        'size': obj.size,
                        'last_modified': obj.last_modified.isoformat() if obj.last_modified else None,
                        'etag': obj.etag
                    })
            return objects
        except Exception as e:
            logger.error(f"Failed to list objects: {str(e)}")
            return []

    def generate_presigned_url(
        self,
        filename: str,
        content_type: str,
        size: int,
        expires_in: int = 3600
    ) -> Dict[str, Any]:
        """
        Generate a pre-signed PUT URL for uploading files directly to TOS.
        
        Args:
            filename: Name of the file to upload
            content_type: MIME type of the file
            size: Size of the file in bytes
            expires_in: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Dictionary containing uploadUrl, publicUrl, key, and expiresAt
        """
        # Generate unique key for the object
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(filename.encode()).hexdigest()[:8]
        key = f"uploads/{timestamp}_{hash_suffix}_{filename}"
        
        # Generate pre-signed URL for PUT operation
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        try:
            pre_signed_url = self.client.pre_signed_url(
                HttpMethodType.Http_Method_Put,
                bucket=self.bucket,
                key=key,
                expires=expires_in,
            )
            
            # Construct public URL (without signature)
            public_url = self._construct_public_url(key)
            
            return {
                "uploadUrl": pre_signed_url.signed_url,
                "publicUrl": public_url,
                "key": key,
                "expiresAt": expires_at.isoformat(),
            }
        except Exception as e:
            raise Exception(f"Failed to generate pre-signed URL: {str(e)}")
    
    def generate_signed_url(
        self,
        key: str,
        expires_in: int = 3600
    ) -> str:
        """
        Generate a signed GET URL for accessing files from TOS.
        
        Args:
            key: Object key in the bucket
            expires_in: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Signed URL for GET operation
        """
        try:
            signed_url = self.client.pre_signed_url(
                HttpMethodType.Http_Method_Get,
                bucket=self.bucket,
                key=key,
                expires=expires_in,
            )
            return signed_url.signed_url
        except Exception as e:
            raise Exception(f"Failed to generate signed URL: {str(e)}")
    
    def _construct_public_url(self, key: str) -> str:
        """
        Construct the public URL for an object.
        
        Args:
            key: Object key in the bucket
            
        Returns:
            Public URL string
        """
        # Ensure key doesn't start with slash
        if key.startswith('/'):
            key = key.lstrip('/')
            
        if self.endpoint:
            # Use virtual-host style as seen in old backend
            return f"https://{self.bucket}.{self.endpoint}/{key}"
        else:
            # Construct default endpoint
            return f"https://{self.bucket}.tos-{self.region}.bytepluses.com/{key}"
    
    def delete_object(self, key: str) -> bool:
        """
        Delete an object from TOS.
        
        Args:
            key: Object key to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_object(self.bucket, key)
            return True
        except Exception as e:
            print(f"Failed to delete object {key}: {str(e)}")
            return False

    def configure_cors(self) -> bool:
        """
        Configure CORS for the bucket to allow requests from common dev origins.
        """
        try:
            from tos.models2 import CORSRule
            
            rules = [
                CORSRule(
                    allowed_origins=["*"],
                    allowed_methods=["GET", "PUT", "POST", "DELETE", "HEAD"],
                    allowed_headers=["*"],
                    expose_headers=["ETag", "x-tos-request-id"],
                    max_age_seconds=3600
                )
            ]
            
            self.client.put_bucket_cors(self.bucket, rules)
            logger.info(f"CORS configured successfully for bucket: {self.bucket}")
            return True
        except Exception as e:
            logger.error(f"Failed to configure CORS: {str(e)}")
            return False


# Singleton instance
_tos_service = None


def get_tos_service() -> TOSService:
    """Get or create TOS service singleton instance."""
    global _tos_service
    if _tos_service is None:
        _tos_service = TOSService()
    return _tos_service
import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import services
from services.tos_service import get_tos_service
from services.llm_service import get_llm_service
from utils.file_utils import save_link_to_txt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


# Error handlers
@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors."""
    return jsonify({"error": "Bad Request", "message": str(error)}), 400


@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    return jsonify({"error": "Not Found", "message": str(error)}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal Server Error", "message": str(error)}), 500


# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "vision-analyzer-backend"
    }), 200


# TOS endpoints
@app.route('/api/tos/presigned-url', methods=['POST'])
def get_presigned_url():
    """
    Generate a pre-signed PUT URL for uploading files directly to TOS.
    
    Request body:
        {
            "filename": "image.jpg",
            "contentType": "image/jpeg",
            "size": 123456
        }
    
    Response:
        {
            "uploadUrl": "https://...",
            "publicUrl": "https://...",
            "key": "uploads/...",
            "expiresAt": "2024-01-01T00:00:00"
        }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        filename = data.get('filename')
        content_type = data.get('contentType')
        size = data.get('size')
        
        if not filename:
            return jsonify({"error": "filename is required"}), 400
        if not content_type:
            return jsonify({"error": "contentType is required"}), 400
        if not size or not isinstance(size, int):
            return jsonify({"error": "size is required and must be an integer"}), 400
        
        logger.info(f"Generating presigned URL for {filename} ({size} bytes)")
        
        # Get TOS service and generate presigned URL
        tos_service = get_tos_service()
        result = tos_service.generate_presigned_url(
            filename=filename,
            content_type=content_type,
            size=size,
        )
        
        logger.info(f"Generated presigned URL for key: {result['key']}")
        return jsonify(result), 200
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": "Validation Error", "message": str(e)}), 400
    except Exception as e:
        logger.error(f"Error generating presigned URL: {str(e)}")
        return jsonify({"error": "Failed to generate presigned URL", "message": str(e)}), 500


@app.route('/api/tos/upload-complete', methods=['POST'])
def upload_complete():
    """
    Notify backend that upload is complete and save link to txt file.
    
    Request body:
        {
            "key": "uploads/...",
            "filename": "image.jpg"
        }
    
    Response:
        {
            "success": true,
            "message": "Link saved successfully",
            "txtPath": "temp/image.jpg.txt"
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        key = data.get('key')
        filename = data.get('filename')
        
        if not key:
            return jsonify({"error": "key is required"}), 400
        if not filename:
            return jsonify({"error": "filename is required"}), 400
        
        logger.info(f"Upload complete for key: {key}")
        
        # Get TOS service to construct public URL
        tos_service = get_tos_service()
        public_url = tos_service._construct_public_url(key)
        
        # Save link to txt file
        txt_path = save_link_to_txt(filename, public_url)
        
        logger.info(f"Link saved to: {txt_path}")
        return jsonify({
            "success": True,
            "message": "Link saved successfully",
            "txtPath": txt_path,
            "publicUrl": public_url
        }), 200
        
    except Exception as e:
        logger.error(f"Error saving link: {str(e)}")
        return jsonify({"error": "Failed to save link", "message": str(e)}), 500


# LLM endpoints
@app.route('/api/llm/analyze', methods=['POST'])
def analyze_image():
    """
    Analyze an image using BytePlus Seed LLM.
    
    Request body:
        {
            "imageUrl": "https://...",
            "prompt": "Describe this image",
            "systemPrompt": "You are a helpful assistant"
        }
    
    Response:
        {
            "content": "The image shows...",
            "model": "seed-2-0-code-preview-260328",
            "usage": {
                "inputTokens": 412,
                "outputTokens": 188,
                "totalTokens": 600
            }
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        image_url = data.get('imageUrl')
        prompt = data.get('prompt')
        system_prompt = data.get('systemPrompt')
        
        if not image_url:
            return jsonify({"error": "imageUrl is required"}), 400
        
        # prompt is now optional as it is handled by the service default if empty
        
        logger.info(f"Analyzing image: {image_url}")
        
        # Get TOS service to generate signed URL
        tos_service = get_tos_service()
        
        # Extract key from public URL
        # Format: https://bucket.tos-region.bytepluses.com/uploads/...
        key = image_url.split("/uploads/")[-1] if "/uploads/" in image_url else image_url.split("/")[-1]
        key = f"uploads/{key}" if not key.startswith("uploads/") else key
        
        # Generate signed URL
        signed_url = tos_service.generate_signed_url(key)
        logger.info(f"Generated signed URL for key: {key}")
        
        # Get LLM service and analyze image with signed URL
        llm_service = get_llm_service()
        result = llm_service.analyze_image(
            image_url=signed_url,
            prompt=prompt,
            system_prompt=system_prompt,
        )
        
        logger.info(f"Analysis complete. Model: {result['model']}")
        return jsonify(result), 200
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": "Validation Error", "message": str(e)}), 400
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        return jsonify({"error": "Failed to analyze image", "message": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'
    
    logger.info(f"Starting Vision Analyzer Backend on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
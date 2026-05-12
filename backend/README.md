# Vision Analyzer Backend

Flask backend for Vision Analyzer application with BytePlus TOS and Seed LLM integration.

## 🚀 Features

- ✅ Pre-signed URL generation for direct TOS uploads
- ✅ Signed URL generation for secure TOS access
- ✅ Image analysis with BytePlus Seed LLM
- ✅ File link storage in local txt files
- ✅ CORS enabled for frontend integration
- ✅ Comprehensive error handling and logging

## 📋 Prerequisites

- Python 3.8+
- BytePlus TOS account
- BytePlus Ark API key for Seed LLM

## 🔧 Installation

1. **Navigate to backend directory**:
```bash
cd backend
```

2. **Create virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**:
```bash
cp .env.example .env
```

5. **Edit `.env` file** with your credentials:
```env
# BytePlus TOS Configuration
TOS_ACCESS_KEY_ID=your_tos_access_key_id
TOS_SECRET_ACCESS_KEY=your_tos_secret_access_key
TOS_REGION=ap-southeast-1
TOS_BUCKET=your_bucket_name
TOS_ENDPOINT=your_tos_endpoint

# BytePlus Seed LLM Configuration
ARK_API_KEY=your_ark_api_key
ARK_BASE_URL=https://ark.ap-southeast.bytepluses.com/api/v3
ARK_MODEL=seed-2-0-code-preview-260328

# Flask Configuration
FLASK_ENV=development
FLASK_PORT=5000
```

## 🏃 Running the Server

### Development Mode
```bash
python app.py
```

Or with Flask directly:
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

### Production Mode
Use a production WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📡 API Endpoints

### Health Check
```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "service": "vision-analyzer-backend"
}
```

### Generate Pre-signed URL
```
POST /api/tos/presigned-url
Content-Type: application/json
```

Request:
```json
{
  "filename": "image.jpg",
  "contentType": "image/jpeg",
  "size": 123456
}
```

Response:
```json
{
  "uploadUrl": "https://...",
  "publicUrl": "https://...",
  "key": "uploads/20240101_120000_a1b2c3d4_image.jpg",
  "expiresAt": "2024-01-01T13:00:00"
}
```

### Upload Complete Notification
```
POST /api/tos/upload-complete
Content-Type: application/json
```

Request:
```json
{
  "key": "uploads/20240101_120000_a1b2c3d4_image.jpg",
  "filename": "image.jpg"
}
```

Response:
```json
{
  "success": true,
  "message": "Link saved successfully",
  "txtPath": "temp/image.jpg.txt",
  "publicUrl": "https://..."
}
```

### Analyze Image
```
POST /api/llm/analyze
Content-Type: application/json
```

Request:
```json
{
  "imageUrl": "https://...",
  "prompt": "Describe this image in detail",
  "systemPrompt": "You are a helpful vision assistant"
}
```

Response:
```json
{
  "content": "The image shows...",
  "model": "seed-2-0-code-preview-260328",
  "usage": {
    "inputTokens": 412,
    "outputTokens": 188,
    "totalTokens": 600
  }
}
```

## 📁 Project Structure

```
backend/
├── app.py                    # Flask application
├── services/
│   ├── tos_service.py        # BytePlus TOS SDK integration
│   └── llm_service.py        # BytePlus Seed LLM integration
├── utils/
│   └── file_utils.py         # File utilities for txt storage
├── temp/                     # Directory for txt files (auto-created)
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
└── README.md               # This file
```

## 🔐 Security Notes

1. **Never commit `.env` file** to version control
2. **Use strong API keys** and rotate them regularly
3. **Set appropriate CORS origins** in production
4. **Use HTTPS** in production
5. **Implement rate limiting** for API endpoints
6. **Add authentication** for production deployment

## 🐛 Troubleshooting

### ImportError: No module named 'tos'
```bash
pip install tos-python-sdk
```

### ImportError: No module named 'openai'
```bash
pip install openai
```

### Missing environment variables
Make sure `.env` file exists and contains all required variables.

### TOS connection errors
- Verify TOS credentials are correct
- Check bucket exists and is accessible
- Ensure region and endpoint are correct

### LLM API errors
- Verify ARK_API_KEY is valid
- Check ARK_MODEL exists and is accessible
- Ensure network can reach BytePlus API

## 📝 Development Tips

1. **Enable debug mode** for detailed error messages:
```env
FLASK_ENV=development
```

2. **Check logs** for debugging:
```bash
# Logs are printed to console
# Check for ERROR and WARNING messages
```

3. **Test endpoints** with curl:
```bash
# Health check
curl http://localhost:5000/health

# Generate presigned URL
curl -X POST http://localhost:5000/api/tos/presigned-url \
  -H "Content-Type: application/json" \
  -d '{"filename":"test.jpg","contentType":"image/jpeg","size":123456}'
```

## 🚢 Deployment

### Docker (Recommended)
Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p temp

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t vision-analyzer-backend .
docker run -p 5000:5000 --env-file .env vision-analyzer-backend
```

### Cloud Platforms
- **Heroku**: Use Procfile with `web: gunicorn app:app`
- **Railway**: Set environment variables in dashboard
- **AWS**: Deploy to EC2 or ECS
- **GCP**: Deploy to Cloud Run

## 📄 License

MIT License - See main project LICENSE file

## 🤝 Contributing

Contributions are welcome! Please follow the main project's contributing guidelines.
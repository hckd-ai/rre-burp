#!/usr/bin/env python3
"""
Run the Video Discovery API server.
"""

import uvicorn
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from api.server import app

if __name__ == "__main__":
    print("🚀 Starting Video Discovery API Server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("=" * 50)
    
    uvicorn.run(
        "api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 
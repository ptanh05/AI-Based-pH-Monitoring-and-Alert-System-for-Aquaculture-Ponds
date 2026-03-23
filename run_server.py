"""
Quick start script for running the web server
"""

import uvicorn

if __name__ == "__main__":
    print("=" * 70)
    print("  Starting pH Monitoring System Web Server")
    print("=" * 70)
    print("  Dashboard: http://localhost:8000")
    print("  API Docs:  http://localhost:8000/docs")
    print("=" * 70)
    print()
    
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=True)


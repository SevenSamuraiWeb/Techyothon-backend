from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app):
    """
    Setup CORS middleware for the FastAPI app
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify your frontend URL
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


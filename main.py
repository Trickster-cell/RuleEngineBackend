from fastapi import FastAPI
from config import settings
from fastapi.middleware.cors import CORSMiddleware
from Routes.RuleNodes import router as RuleRouter


app = FastAPI(title="Backend for AST based Rule Engine")

# Configure CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from all origins
    allow_credentials=True,  # Allow credentials to be included
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include the RuleNodes router with a specified prefix
app.include_router(RuleRouter, prefix="/rule")


@app.get("/")
async def read_root():
    """Root endpoint returning a welcome message."""
    return {"message": "AST Engine"}

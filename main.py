from fastapi import FastAPI
from config import settings
from fastapi.middleware.cors import CORSMiddleware


from Routes.RuleNodes import router as RuleRouter


app = FastAPI(title="Backend for AST based Rule Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(RuleRouter, prefix="/rule")


@app.get("/")
async def read_root():
    return {"message": "AST Engine"}
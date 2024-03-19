import uvicorn
from fastapi import FastAPI, APIRouter

from api.handlers import user_router

# -- APP INSTANCE --
app = FastAPI(title="edu_platform")


main_api_router = APIRouter()
main_api_router.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(main_api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

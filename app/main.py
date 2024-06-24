from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from .routes.line_callball_route import line_bot_callback_router
from .routes.greeting import greeting_router


def get_application() -> FastAPI:
    app = FastAPI(
        prefix="/api/v1",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(line_bot_callback_router)
    app.include_router(greeting_router)
    return app


app: FastAPI = get_application()


if __name__ == "__main__":
    uvicorn.run(
        "__main__:app",
    )

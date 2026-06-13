"""Entrypoint for running the Evidence Service."""

from mctagents.api.config import settings

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "mctagents.api.app:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
        reload=True,
    )

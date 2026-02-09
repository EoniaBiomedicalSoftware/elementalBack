from .elemental.settings import init_settings
from .elemental.cover import get_cover
from .settings import ApplicationSettings

app_settings = ApplicationSettings() # noqa
init_settings(app_settings)

def run(runtime: str):
    VALID_MODES = {"cli", "web"}
    if runtime not in VALID_MODES:
        raise ValueError(f"Invalid runtime mode: '{runtime}'. Use 'cli' or 'web'.")

    get_cover(
        runtime=runtime
    )

    if runtime == 'cli':
        ...

    elif runtime == 'web':
        import uvicorn

        if app_settings.application.debug:
            uvicorn.run(
                "app.gateways.web:app",
                host=app_settings.application.host,
                port=app_settings.application.port,
                reload=True,
                access_log=False
            )
        else:
            from .gateways.web import app

            uvicorn.run(
                app,
                host=app_settings.application.host,
                port=app_settings.application.port,
            )

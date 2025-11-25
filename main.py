from app.controllers.cli import main_cli
import sentry_sdk
import os

# Initialize Sentry for error tracking
sentry_sdk.init(
    dsn=os.getenv('DSN'),
    traces_sample_rate=1.0,  # Pour du monitoring de performance (optionnel)
    environment="development",
    send_default_pii=True,
)

if __name__ == "__main__":
    main_cli()

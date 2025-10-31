from app.commands.cli import main_cli
import sentry_sdk

# Initialize Sentry for error tracking
sentry_sdk.init(
    dsn="https://2b360dacc8e1eaa1d57d6a8762c8d739@o4510284494798848.ingest.de.sentry.io/4510284496568400",
    traces_sample_rate=1.0,  # Pour du monitoring de performance (optionnel)
    environment="development",
    send_default_pii=True,
)

if __name__ == "__main__":
    main_cli()

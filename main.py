from app.controllers.cli import main_cli
import sentry_sdk

# Initialize Sentry for error tracking
sentry_sdk.init(
    dsn="https://62d38b9821ba182f35b8eaa1882384be@o4510284494798848.ingest.de.sentry.io/4510421483454544",
    traces_sample_rate=1.0,  # Pour du monitoring de performance (optionnel)
    environment="development",
    send_default_pii=True,
)

if __name__ == "__main__":
    main_cli()

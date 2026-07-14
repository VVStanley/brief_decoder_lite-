import os
from pathlib import Path

from dynaconf import Dynaconf

# Base directory for the backend (brief_decoder_lite/backend)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

_settings = Dynaconf(
    envvar_prefix="APP",
    settings_files=[
        str(BASE_DIR / "config" / "settings.toml"),
        str(BASE_DIR / "config" / ".secrets.toml"),
    ],
    environments=True,
    load_dotenv=True,
    env_switcher="ENV_FOR_DYNACONF",
    default_env="default",
    env="local",
    sysenv_fallback=True,
    silent_errors=True,
)


class AppSettings:
    """Typed settings wrapper for Dynaconf configuration.

    Provides IDE autocomplete and compatibility with static analyzers.
    Prioritizes OS environment variables directly for production and CI/CD support.
    """

    @property
    def DATABASE_URL(self) -> str:
        # Check direct OS env first (e.g. injected in CI/CD or prod), then fallback to Dynaconf
        return os.environ.get("DATABASE_URL") or str(_settings.get("DATABASE_URL"))

    @property
    def LLM_PROVIDER(self) -> str:
        return os.environ.get("LLM_PROVIDER") or str(_settings.get("LLM_PROVIDER"))

    @property
    def GEMINI_API_KEY(self) -> str:
        return os.environ.get("GEMINI_API_KEY") or str(_settings.get("GEMINI_API_KEY"))

    @property
    def GEMINI_MODEL(self) -> str:
        return os.environ.get("GEMINI_MODEL") or str(
            _settings.get("GEMINI_MODEL", "gemini-flash-latest")
        )

    @property
    def SENTRY_DSN(self) -> str:
        return os.environ.get("SENTRY_DSN") or str(_settings.get("SENTRY_DSN", ""))

    @property
    def SENTRY_TRACES_SAMPLE_RATE(self) -> float:
        val = os.environ.get("SENTRY_TRACES_SAMPLE_RATE") or _settings.get(
            "SENTRY_TRACES_SAMPLE_RATE", 1.0
        )
        try:
            return float(val)
        except (ValueError, TypeError):
            return 1.0

    @property
    def LLM_MAX_ATTEMPTS(self) -> int:
        val = os.environ.get("LLM_MAX_ATTEMPTS") or _settings.get("LLM_MAX_ATTEMPTS", 3)
        try:
            return int(val)
        except (ValueError, TypeError):
            return 3

    @property
    def LLM_TIMEOUT(self) -> float:
        val = os.environ.get("LLM_TIMEOUT") or _settings.get("LLM_TIMEOUT", 45.0)
        try:
            return float(val)
        except (ValueError, TypeError):
            return 45.0

    @property
    def CLEANUP_TIMEOUT_MINUTES(self) -> int:
        val = os.environ.get("CLEANUP_TIMEOUT_MINUTES") or _settings.get(
            "CLEANUP_TIMEOUT_MINUTES", 3
        )
        try:
            return int(val)
        except (ValueError, TypeError):
            return 3

    @property
    def current_env(self) -> str:
        return os.environ.get("ENV_FOR_DYNACONF") or str(_settings.current_env)


settings = AppSettings()

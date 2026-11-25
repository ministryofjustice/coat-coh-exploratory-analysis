import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from uuid import UUID


ROOT = Path.cwd()
DASHBOARD = os.environ.get("DASHBOARD")

if not DASHBOARD:
    raise RuntimeError("Missing required environment variable: DASHBOARD")

APP = ROOT / DASHBOARD / "app.py"

if not APP.is_file():
    raise RuntimeError(f"Dashboard app not found: {APP}")


def required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value or not value.strip():
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def build_auth_config() -> dict[str, dict[str, str]]:
    base_url = required_env("APP_BASE_URL").rstrip("/")
    tenant_id = str(UUID(required_env("ENTRA_TENANT_ID")))
    cookie_secret = required_env("ENTRA_COOKIE_SECRET")

    if len(cookie_secret) < 32:
        raise RuntimeError("ENTRA_COOKIE_SECRET must be at least 32 characters.")

    return {
        "auth": {
            "redirect_uri": f"{base_url}/oauth2callback",
            "cookie_secret": cookie_secret,
        },
        "auth.microsoft": {
            "client_id": required_env("ENTRA_CLIENT_ID"),
            "client_secret": required_env("ENTRA_CLIENT_SECRET"),
            "server_metadata_url": (
                f"https://login.microsoftonline.com/{tenant_id}"
                "/v2.0/.well-known/openid-configuration"
            ),
        },
    }


def main() -> int:
    if os.environ.get("APP_ENV") == "local":
        return subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(APP), *sys.argv[1:]],
            cwd=ROOT,
            check=False,
        ).returncode

    sections = build_auth_config()

    # Streamlit reads authentication settings from a secrets file.
    with tempfile.TemporaryDirectory(prefix="coat-auth-") as directory:
        secrets_path = Path(directory) / "secrets.toml"
        descriptor = os.open(
            secrets_path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )

        with os.fdopen(descriptor, "w", encoding="utf-8") as file:
            for section, settings in sections.items():
                file.write(f"[{section}]\n")
                for key, value in settings.items():
                    file.write(f"{key} = {json.dumps(value)}\n")
                file.write("\n")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(APP),
                "--secrets.files",
                str(secrets_path),
                *sys.argv[1:],
            ],
            cwd=ROOT,
            check=False,
        )
        return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
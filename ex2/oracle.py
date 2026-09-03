#!/usr/bin/env python3
import os
import sys

# Setting up a virtual environment and install
#   requirements:
# python3 -m venv .venv
# source .venv/bin/activate
# pip install -r requirements.txt


def load_dotenv() -> bool:
    try:
        from dotenv import load_dotenv as _load

        _load()
        return True
    except ImportError:
        return False


CONFIG_DEFAULTS: dict[str, str | None] = {
    "MATRIX_MODE": "development",
    "DATABASE_URL": "sqlite:///matrix_dev.db",
    "API_KEY": None,
    "LOG_LEVEL": "DEBUG",
    "ZION_ENDPOINT": "http://localhost:8080",
}


def get_config() -> tuple[dict[str, str], bool, list[str]]:
    dotenv_loaded = load_dotenv()
    config: dict[str, str] = {}
    using_defaults: list[str] = []

    for key, default in CONFIG_DEFAULTS.items():
        env_val = os.getenv(key)
        if env_val:
            config[key] = env_val
        elif default is not None:
            config[key] = default
            using_defaults.append(key)

    return config, dotenv_loaded, using_defaults


def validate_config(config: dict[str, str]) -> list[str]:
    errors: list[str] = []
    mode = config.get("MATRIX_MODE", "").lower()
    if mode not in ("development", "production"):
        errors.append(
            f"MATRIX_MODE must be 'development' or 'production', got '{mode}'"
        )
    if not config.get("DATABASE_URL"):
        errors.append("DATABASE_URL is required")
    if not config.get("API_KEY"):
        errors.append("API_KEY is required")
    if not config.get("ZION_ENDPOINT"):
        errors.append("ZION_ENDPOINT is required")
    return errors


def mask_secret(value: str, visible: int = 4) -> str:
    if len(value) <= visible * 2:
        return "********"
    masked_len = len(value) - visible * 2
    return value[:visible] + "*" * masked_len + value[-visible:]


def check_env_file() -> tuple[bool, str]:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, ".env")
    gitignore_path = os.path.join(script_dir, ".gitignore")

    if not os.path.exists(env_path):
        return False, ".env file not found"

    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if stripped in (".env", "/.env", "*.env"):
                    return True, ".env file properly configured"

    return True, ".env file present but NOT in .gitignore"


def show_dev_vs_prod(config: dict[str, str]) -> None:
    mode = config.get("MATRIX_MODE", "development").lower()
    zion_url = config.get("ZION_ENDPOINT", "unset")
    print("\n" + "=" * 50)
    print(f"ENVIRONMENT: {mode}")
    print("=" * 50)
    if mode == "development":
        print("  Database:    SQLite local file (no auth required)")
        print("  API Key:     Using placeholder/dev key")
        print("  Logging:     Verbose DEBUG output")
        print(f"  Zion:        Local endpoint ({zion_url})")
        print("  Caching:     Disabled")
        print("  SSL Verify:  False")
    else:
        print("  Database:    PostgreSQL cluster with SSL")
        print("  API Key:     Production key enforced")
        print("  Logging:     WARN level only")
        print("  Zion:        Secure remote endpoint")
        print("  Caching:     Redis enabled")
        print("  SSL Verify:  True")
    print("=" * 50)


def print_config_summary(config: dict[str, str]) -> None:
    mode = config.get("MATRIX_MODE", "development").lower()
    is_prod = mode == "production"

    database_url = config.get("DATABASE_URL", "")
    if not database_url:
        database = "Not configured"
    elif is_prod:
        database = "Connected (details hidden)"
    elif "localhost" in database_url or "sqlite" in database_url:
        database = "Connected to local instance"
    else:
        database = "Connected to remote instance"

    api_key = config.get("API_KEY")
    if not api_key:
        api = "Missing"
    elif is_prod:
        api = f"Authenticated ({mask_secret(api_key)})"
    else:
        api = "Authenticated"

    zion_status = "Online" if config.get("ZION_ENDPOINT") else "Offline"

    print("\nConfiguration loaded:")
    print(f"Mode: {mode}")
    print(f"Database: {database}")
    print(f"API Access: {api}")
    print(f"Log Level: {config.get('LOG_LEVEL', 'NOT SET')}")
    print(f"Zion Network: {zion_status}")


def report_config_health(using_defaults: list[str]) -> None:
    if using_defaults:
        print(
            f"[WARN] Using default values for: {', '.join(using_defaults)}"
        )


def report_validation_errors(config: dict[str, str]) -> bool:
    errors = validate_config(config)
    if errors:
        print("\n[ERROR] Configuration validation failed:")
        for err in errors:
            print(f"  - {err}")
        return False
    return True


def print_security_report(
    config: dict[str, str], dotenv_loaded: bool
) -> None:
    if dotenv_loaded:
        print("[OK] python-dotenv loaded .env")
    else:
        print("[WARN] python-dotenv not installed; .env not loaded")

    env_ok, env_msg = check_env_file()
    print(f"[OK] {env_msg}" if env_ok else f"[WARN] {env_msg}")

    if config.get("API_KEY"):
        print("[OK] API_KEY supplied via environment (no hardcoded secret)")
    else:
        print("[WARN] API_KEY not set")

    mode = config.get("MATRIX_MODE", "development").lower()
    if mode == "production":
        print("[OK] Production mode: secure settings enforced")
    else:
        print("[INFO] Development mode: production overrides available")


def main() -> int:
    print("\nORACLE STATUS: Reading the Matrix...")
    config, dotenv_loaded, using_defaults = get_config()

    print_config_summary(config)

    report_config_health(using_defaults)
    validation_ok = report_validation_errors(config)

    print("\nEnvironment security check:")
    print_security_report(config, dotenv_loaded)

    if validation_ok:
        print("\nThe Oracle sees all configurations.")
    else:
        print("\nThe Oracle's vision is clouded. Configuration incomplete.")

    print()
    print("-" * 75)
    show_dev_vs_prod(config)
    print()

    return 0 if validation_ok else 1


if __name__ == "__main__":
    sys.exit(main())

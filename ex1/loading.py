#!/usr/bin/env python3

import sys
from importlib.metadata import PackageNotFoundError, version

REQUIRED_PACKAGES: dict[str, str] = {
    "pandas": "Data manipulation ready",
    "numpy": "Numerical computation ready",
    "matplotlib": "Visualization ready",
}


def check_dependencies() -> tuple[list[tuple[str, str, str]], list[str]]:
    installed: list[tuple[str, str, str]] = []
    missing: list[str] = []

    for package, description in REQUIRED_PACKAGES.items():
        try:
            v = version(package)
        except PackageNotFoundError:
            missing.append(package)
        else:
            installed.append((package, v, description))

    return installed, missing


def print_loading_status(
    installed: list[tuple[str, str, str]], missing: list[str]
) -> None:
    print("\nLOADING STATUS: Loading programs...\n")
    print("Checking dependencies:")
    for package, v, description in installed:
        print(f"[OK] {package} ({v}) - {description}")
    for package in missing:
        print(f"[NOT FOUND] {package} - not installed")


# Make sure tht Poetry is installed, `pipx install poetry`
# before using Poetry
def print_install_instructions(missing: list[str]) -> None:
    if not missing:
        return

    print(f"\n[ERROR]: {len(missing)} package(s) missing: "
          f"{', '.join(missing)}\n")
    print("Make sure you are in the virtual environment")
    print("(its prefix should show in your terminal prompt).\n")
    print("To load the programs, run:")
    print("  pip install -r requirements.txt      # with pip")
    print("  poetry install                       # with poetry\n")
    print("Then run this program again.")


def run_analysis(n_points: int, output_path: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    print("\nAnalyzing Matrix data...")
    rng = np.random.default_rng()
    glitch = rng.normal(loc=100, scale=15, size=n_points)

    print(f"Processing {n_points} data points...")
    df = pd.DataFrame({"glitch": glitch})
    median = df["glitch"].median()
    std = df["glitch"].std()
    print("Generating visualization...")

    plt.hist(df["glitch"], bins=30, orientation="horizontal")
    plt.axhline(median, color="blue", label=f"Median: {median:.2f}")
    plt.axhline(
        median - std, color="orange", linestyle="--",
        label=f"-1 STD: {median - std:.2f}"
    )
    plt.axhline(
        median + std, color="orange", linestyle="--",
        label=f"+1 STD: {median + std:.2f}"
    )
    plt.title("Matrix Analysis")
    plt.xlabel("Frequency")
    plt.ylabel("Glitch")
    plt.legend()
    plt.savefig(output_path)
    plt.close()

    print("\nAnalysis complete!")
    print(f"Results saved to: {output_path}")


def read_requirements_constraints(
        path: str = "requirements.txt") -> dict[str, str]:
    constraints: dict[str, str] = {}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                for pkg in REQUIRED_PACKAGES:
                    if line.startswith(pkg):
                        constraints[pkg] = line
    except FileNotFoundError:
        pass
    return constraints


def read_pyproject_constraints(path: str = "pyproject.toml") -> dict[str, str]:
    constraints: dict[str, str] = {}
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return constraints

    in_block = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("dependencies") and not in_block:
            in_block = True
            continue
        if in_block:
            if stripped == "]":
                in_block = False
                continue
            req = stripped.strip('",')
            for pkg in REQUIRED_PACKAGES:
                if req.startswith(pkg):
                    constraints[pkg] = req
    return constraints


def compare_managers() -> None:
    print("-" * 50)
    print("Comparision: pip vs Poetry")

    pip_constraints = read_requirements_constraints()
    poetry_constraints = read_pyproject_constraints()

    header = (
        f"{'Package':<12} {'Installed':<10} "
        f"{'pip(requirements.txt)':<24} Poetry(pyproject.toml)"
    )
    print(header)
    for name in REQUIRED_PACKAGES:
        v = version(name)
        pip_pin = pip_constraints.get(name, f"{name}=={v} (not found)")
        poetry_pin = poetry_constraints.get(name, f'{name} (not found)')
        print(f"{name:<12} {v:<10} {pip_pin:<24} {poetry_pin}")
    print()

    print("pip  -> requirements.txt")
    print("  - Transitive dependencies pulled in by pandas/numpy/"
          "matplotlib.")
    print("  - Installs are fully reproducible but never "
          "update on their own.")
    print("  - To install: `pip install -r requirements.txt`\n")

    print("poetry -> pyproject.toml")
    print("  - Lists only the packages you actually asked for, with")
    print("     minimums (i.e. >= any compatible version).")
    print("  - Poetry resolves the rest and records the exact result in")
    print("     poetry.lock, keeping stated intent and locked outcome "
          "separate.")
    print("  - To install: `poetry install`")
    print("  - To run: `poetry run python loading.py`")
    print()


def main() -> int:
    installed, missing = check_dependencies()
    print_loading_status(installed, missing)

    if missing:
        print_install_instructions(missing)
        return 1

    size = 1000
    dst = "matrix_analysis.png"
    run_analysis(size, dst)
    print("\n")
    compare_managers()

    return 0


if __name__ == "__main__":
    sys.exit(main())

import os
import sys
import site


# sys.prefix:      the path to the current Python interpreter is installed.
# sys.base_prefix: the location if the Python interpreter outside of a virtual
#                  environment
# if sys.prefix & sys.base_prefix are the same then the code is not running
#   inside of a virtual environment
#
def in_virtual_env():
    return sys.prefix != sys.base_prefix


def main():
    print()
    if in_virtual_env():
        print("MATRIX STATUS:  Welcome to the construct\n")
        print(f"Current Python: {os.path.realpath(sys.executable)}")
        venv_path = sys.prefix
        venv_name = os.path.basename(venv_path)
        print(f"Virtual environment: {venv_name}")
        print(f"Environment Path: {venv_path}")
        print()
        print("SUCCESS:  You're in an isolated environment!")
        print("Safe to install packages without affecting the global system")
        print()
        print("Package installation path:")
        path_package = site.getsitepackages()
        print(path_package[0])
        print()
    else:
        print("MATRIX STATUS:  You're still plugged in\n")
        print(f"Current Python: {os.path.realpath(sys.executable)}")
        print("Virtual environment: None detected")
        print()
        print("WARNING:  You're in the global environment!")
        print("The machines see everything you install")
        print()
        print("To enter the construct, run:")
        print("python -m venv matrix_env")
        print("source matrix_env/bin/activate # On Unix")
        print("matrix_env\\Scripts\\activate # On Windows")
        print()
        print("Then run this program again.")
        print()


if __name__ == "__main__":
    main()

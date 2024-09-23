import argparse
import os
import subprocess


def main():
    parser = argparse.ArgumentParser(
        description="Post install setup script's arguments"
    )
    parser.add_argument("dialer", help="Provide dialer name")

    # Path to the bash script
    script_path = os.path.join(os.path.dirname(__file__), 'post_install.sh')

    # Run the bash script with the argument
    subprocess.run(
        ['bash', script_path, parser.parse_args().dialer],
        check=True
    )

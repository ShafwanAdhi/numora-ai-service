import argparse
import logging

import uvicorn
from dotenv import load_dotenv

from .api import create_app
from .bridge import ROOT


def main():
    parser = argparse.ArgumentParser(description="Authenticated Numora compute HTTP service")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8770)
    args = parser.parse_args()
    load_dotenv(ROOT / ".env", override=False)
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("numora.generator").setLevel(logging.INFO)
    uvicorn.run(create_app(), host=args.host, port=args.port, access_log=False, log_level="warning")


if __name__ == "__main__":
    main()

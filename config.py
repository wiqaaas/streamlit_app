# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

BASE = Path(__file__).parent
load_dotenv(BASE / ".env")

ELEARNING_SOURCE = os.getenv("ELEARNING_SOURCE")
SCHEDULE_SOURCE  = os.getenv("SCHEDULE_SOURCE")
MATCHES_SOURCE   = os.getenv("MATCHES_SOURCE")
TOKEN_THRESHOLD  = 900_000  # 900k for gpt-4.1-mini

USE_CONTEXT  = True
USE_EXAMPLES = True

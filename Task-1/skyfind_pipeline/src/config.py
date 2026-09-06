from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_NAME = "kunyu241/SkyFind"

SPLITS = [
    "train",
    "validation",
    "test",
    "train_aug"
]

DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
REPORT_DIR = BASE_DIR / "reports"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

LOG_INTERVAL = 10000
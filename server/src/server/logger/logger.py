import logging
from pathlib import Path

# Resole to src/server
log_file = Path(__file__).parent.parent / "server_debug.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"Logger initialized. Logs will be written to: {log_file}")

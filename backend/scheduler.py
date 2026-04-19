import schedule
import time
import logging
import subprocess
import os
from datetime import datetime

logging.basicConfig(
    filename="scheduler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
CLI_COMMAND = 'python cli.py --name "NextGen Solutions" --url "https://www.ibm.com"'

def job_run_pipeline():
    logger.info("Scheduler triggered pipeline run.")
    logger.info("Starting pipeline run at %s", datetime.now().isoformat())
    try:
        cwd = os.path.dirname(__file__)
        result = subprocess.run(CLI_COMMAND, shell=True, cwd=cwd, capture_output=True, text=True, timeout=1800)
        logging.info("Pipeline stdout: %s", result.stdout[:1000])
        if result.returncode != 0:
            logging.error("Pipeline failed: %s", result.stderr[:1000])
        else:
            logging.info("Pipeline completed successfully.")
    except Exception as e:
        logging.exception("Error running pipeline: %s", e)

if __name__ == "__main__":
    schedule.every(5).minutes.do(job_run_pipeline)

    logger.info("Scheduler started running pipeline on schedule every 5 minutes.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user.")

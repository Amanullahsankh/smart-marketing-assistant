# scheduler.py
import schedule
import time
import logging
import subprocess
import os
from datetime import datetime

# Optional: log file for scheduler runs
logging.basicConfig(
    filename="scheduler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Change these to your preferred command and args
CLI_COMMAND = 'python cli.py --name "NextGen Solutions" --url "https://www.ibm.com"'

def job_run_pipeline():
    logging.info("Scheduler triggered pipeline run.")
    print("Scheduler: starting pipeline run at", datetime.now().isoformat())
    # Option A: run the CLI in a subprocess (isolates environment)
    try:
        # Ensure working dir is project folder
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
    # For demo: run every 5 minutes. For production change to: schedule.every().week.do(job_run_pipeline)
    schedule.every(5).minutes.do(job_run_pipeline)

    print("Scheduler started — running pipeline on schedule (every 5 minutes for demo). Press Ctrl+C to stop.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("Scheduler stopped by user.")

import logging

logging.basicConfig(filename='app.log', filemode="w", level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s)")


def log_info(text):
    print(f"{text}")
    logging.info(text)


def log_warn(text):
    print(f"[WARN] {text}")
    logging.info(text)


def log_error(text):
    print(f"[ERROR] {text}")
    logging.error(text)

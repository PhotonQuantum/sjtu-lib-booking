import json
import logging
import sys

from .booking import BookingManager

logging.basicConfig(level=logging.INFO)


def main():
    config_path = sys.argv[1]
    with open(config_path) as f:
        users = json.load(f)
    for username, password in users.items():
        logging.info(f"[{username}] Booking seat...")
        try:
            manager = BookingManager(username, password)
            reservation_id = manager.book()
            logging.info(f"[{username}] Reservation id: {reservation_id}"
                         if reservation_id else f"[{username}] No reservation id found. Ignored.")
        except Exception:
            logging.exception(f"[{username}] Exception occur.")
    logging.info("Done.")


if __name__ == "__main__":
    main()

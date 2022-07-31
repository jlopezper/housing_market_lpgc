import logging
from housingmarketlpgc.gmail import gmail_authenticate
from housingmarketlpgc.body import process_messages, save_data

# from housingmarketlpgc import utils
from housingmarketlpgc.utils import init_logger
from datetime import datetime


logger = init_logger()


def run():
    logger.info(f"### Execution of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ###")
    service = gmail_authenticate(token_file="token.json", cred_file="credentials.json")
    df = process_messages(service=service)
    save_data(df)


if __name__ == "__main__":
    run()

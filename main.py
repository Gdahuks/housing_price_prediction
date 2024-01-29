from dotenv import load_dotenv

load_dotenv()


if __name__ == "__main__":
    # load libraries here to first load .env file
    from data_loaders import collect_and_upload_data

    collect_and_upload_data()

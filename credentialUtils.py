import os
from google.oauth2 import service_account

key_account_path = r"C:\Users\khant\projects\ShakeMap\gen-lang-service-keys.json"

def get_credentials():
    if(not os.path.exists(key_account_path)):
        raise FileNotFoundError(
            f"Service Acc Key File NOT Found."
        )

    return service_account.Credentials.from_service_account_file(key_account_path)


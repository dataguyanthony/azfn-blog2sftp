import azure.functions as func
import logging # For logging
import os  # For accessing environment variables
from azure.identity import DefaultAzureCredential # For Azure Key Vault authentication
from azure.keyvault.secrets import SecretClient # For accessing secrets in Key Vault
from unidecode import unidecode  # For converting non-ASCII characters to ASCII
import paramiko  # For SFTP connection
import time  # For sleep function / retry delay

# Initialize the Azure Function App
app = func.FunctionApp()

# Function to get secrets from Azure Key Vault
def get_secret_from_key_vault(vault_url, secret_name):
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)
    secret = client.get_secret(secret_name)
    return secret.value

@app.blob_trigger(arg_name="myblob", path="${STORAGE_ACCOUNT_FILE_PATH}/{name}", connection="STORAGE_ACCOUNT") 
def ascii2sftp(myblob: func.InputStream):
    # Variables for SFTP connection and retry logic
    vault_url = os.environ["KEY_VAULT_URL"]
    sftp_host = os.environ["SFTP_HOST"]
    sftp_username = os.environ["SFTP_USERNAME"]
    sftp_password_secretname = os.environ["SFTP_PASSWORD_SECRETNAME"]
    sftp_max_retries = 3
    sftp_retry_delay_in_seconds = 15
    
    # Get SFTP password from the Key Vault using the secret name
    sftp_password = get_secret_from_key_vault(vault_url, sftp_password_secretname)

    # Log the blob details
    logging.info(f"Function started for blob: '{myblob.name}' ({myblob.length} bytes)")
    
    # Read the blob content
    blob_content = myblob.read().decode('utf-8')

    # Replace non-ASCII characters with their ASCII equivalents
    ascii_content = unidecode(blob_content)

    # Connect to the SFTP server and upload the ASCII content
    for attempt in range(1, sftp_max_retries + 1):
        try:
            transport = paramiko.Transport((sftp_host, 22))
            transport.connect(username=sftp_username, password=sftp_password)
            sftp = paramiko.SFTPClient.from_transport(transport)

            # Save the ASCII content to a file on the SFTP server
            remote_path = f"/path/to/sftp/directory/{myblob.name}"
            with sftp.file(remote_path, 'w') as remote_file:
                remote_file.write(ascii_content)
            logging.info(f"File successfully uploaded to SFTP: {remote_path}")

            # Close the SFTP connection
            sftp.close()
            transport.close()
            break  # Exit the loop if the upload is successful
        except Exception as e:
            logging.error(f"Attempt {attempt} failed to upload file to SFTP: {e}")
            if attempt < sftp_max_retries:
                logging.info(f"Retrying in {sftp_retry_delay_in_seconds} seconds...")
                time.sleep(sftp_retry_delay_in_seconds)
            else:
                logging.error("All retry attempts failed. Giving up.")

# Azure Function: ASCII SFTP Uploader

This project is an Azure Function that listens for new files uploaded to an Azure Blob Storage container (`aspire-sftp/prod/inbound/EFT`). It processes the files by replacing non-ASCII characters with their ASCII equivalents and uploads the processed files to an SFTP server.

---

## Features
- **Blob Trigger**: Automatically triggers when a new file is uploaded to the specified Azure Blob Storage container.
- **ASCII Conversion**: Converts non-ASCII characters in the file to their ASCII equivalents using the `unidecode` library.
- **SFTP Upload**: Uploads the processed file to a specified SFTP server.
- **Retry Logic**: Retries the SFTP upload up to 3 times with a 15-second delay between attempts.

---

## Prerequisites
1. **Azure CLI**: Install the [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli).
2. **Python**: Install Python 3.9 or later.
3. **Azure Function Core Tools**: Install the [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local).
4. **Git**: Ensure Git is installed on your machine.
5. **Azure Storage Account**: Create an Azure Storage Account for the blob trigger.
6. **Azure Key Vault**: Create an Azure Key Vault to store sensitive credentials (e.g., SFTP password).
7. **SFTP Server**: Ensure you have access to an SFTP server.

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/azfn-ascii-sftp-uploader.git
cd azfn-ascii-sftp-uploader
```

### 2. Create a Python Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r [requirements.txt](http://_vscodecontentref_/2)
```

### 4. Create an Azure Function App
Use the Azure CLI to create an Azure Function App:
```bash
# Variables
RESOURCE_GROUP="<your-resource-group>"
STORAGE_ACCOUNT="<your-storage-account-name>"
FUNCTION_APP="<your-function-app-name>"
LOCATION="<your-region>"  # e.g., eastus

# Create a resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create a storage account
az storage account create --name $STORAGE_ACCOUNT --location $LOCATION --resource-group $RESOURCE_GROUP --sku Standard_LRS

# Create the function app
az functionapp create --resource-group $RESOURCE_GROUP --consumption-plan-location $LOCATION \
    --runtime python --runtime-version 3.9 \
    --functions-version 4 --name $FUNCTION_APP --storage-account $STORAGE_ACCOUNT
```

### 6. Configure Azure Key Vault
Store sensitive credentials in Azure Key Vault:
```bash
az functionapp config appsettings set --name $FUNCTION_APP --resource-group $RESOURCE_GROUP --settings \
    FUNCTIONS_WORKER_RUNTIME=python \
    STORAGE_ACCOUNT="DefaultEndpointsProtocol=https;AccountName=$STORAGE_ACCOUNT;AccountKey=<your-storage-account-key>;EndpointSuffix=core.windows.net" \
    KEY_VAULT_URL="https://$KEY_VAULT_NAME.vault.azure.net/" \
    SFTP_HOST="<your-sftp-host>" \
    SFTP_USERNAME="<your-sftp-username>" \
    SFTP_PASSWORD_SECRETNAME="sftp-password"
```
---

## Local Development
1. Start the Azure Function locally: 
```bash
func start
```
2. Upload a file to the `aspire-sftp/prod/inbound/EFT` container in your Azure Storage Account to trigger the function.

---

## Deployment
1. Authenticate with Azure: 
```bash
az login
```
2. Deploy the function to Azure: 
```bash
func azure functionapp publish $FUNCTION_APP
```

---

## CI/CD Pipeline
This project includes a GitHub Actions workflow for CI/CD. The workflow:
* Installs dependencies.
* Replaces placeholders in local.settings.json with GitHub Secrets.
* Deploys the function to Azure.

### Setting Up GitHub Secrets

Add the following secrets to your GitHub repository:
* `AZURE_CREDENTIALS`: JSON output from `az ad sp create-for-rbac`
* `STORAGE_ACCOUNT_NAME`: Azure Storage Account Name
* `STORAGE_ACCOUNT_KEY`: Azure Storage Account Key
* `STORAGE_ACCOUNT_FILE_PATH`: Container and storage path (don't include a trailing /)
* `KEY_VAULT_NAME`: ame of the Azure Keey Vault with you SFTP Password 
* `SFTP_HOST`: SFTP Host where you need to upload the file
* `SFTP_USERNAME`: SFTP Username user to connect to the SFTP
* `SFTP_PASSWORD_SECRETNAME`: Key Vault secret where the SFTP Password is stored
* `SFTP_UPLOAD_PATH`: / Preceding path on the host of what folder to upload the file to (don't include a trailing /)

---

## Contributing

Feel free to fork this repository and submit pull requests for improvements or bug fixes.

---

## Licence

This project is licensed under the MIT License. See the LICENSE file for details.
To export data from Google Analytics 4 (GA4) using Python, you can utilize the Google Analytics Data API v1. Below is a Python script for exporting data from GA4. This example assumes you have already set up a service account in Google Cloud and downloaded the JSON key file for authentication.
pip install google-analytics-data
Service Account Key File: Ensure that your service account key file is securely stored and its path is correctly specified in SERVICE_ACCOUNT_FILE.
Property ID: Replace YOUR_GA4_PROPERTY_ID with the actual property ID from your GA4 account.
Metrics and Dimensions: Customize the dimensions and metrics as per your requirements.
Date Range: Modify the start_date and end_date parameters to fit your needs.
CSV Export: The data is saved in ga4_data_export.csv in the same directory as the script.
he SERVICE_ACCOUNT_FILE in the script refers to the JSON key file of a service account that has permissions to access the Google Analytics Data API. This file is essential for authentication and should be downloaded from the Google Cloud Console.

Steps to Obtain the SERVICE_ACCOUNT_FILE
Create a Service Account:

Go to the Google Cloud Console.
Navigate to IAM & Admin > Service Accounts.
Click Create Service Account.
Assign Permissions:

Assign the role "Analytics Data Viewer" to the service account.
Create a Key:

After creating the service account, click on it to open the details.
Go to the Keys tab and click Add Key > Create New Key.
Select JSON format and click Create. This downloads the key file to your computer.
Grant Access to the GA4 Property:

Go to your GA4 account.
Navigate to Admin > Account Access Management.
Add the service account's email (found in the JSON file) and assign it Viewer or higher permissions.
Save the JSON File:

Place the downloaded JSON file in a secure directory within your project.
In the script, set SERVICE_ACCOUNT_FILE to the path of this file.

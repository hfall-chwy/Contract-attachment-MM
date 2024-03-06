# Contract-attachment---MM
Chewy Contract Attachment Automation
This Python script automates the process of attaching Excel and PDF files to Chewy contracts through the Chewy MarketMedium API. The script is designed to streamline the attachment of contracts specified in an Excel file to corresponding deals in the Chewy system.
Configuration

Before running the script, make sure to configure the following parameters in the script:

    deal_name: The name of the Chewy deal.
    file_name: The name of the Excel file containing contract information.
    file_path: The path to the Excel file.
    report_folder: The folder path where the success and failed reports will be saved.
    contract_pdf_folder: The folder path where the PDF contracts are located.

Dependencies

The script relies on the following Python libraries:

    os: For handling file paths and directories.
    requests: For making HTTP requests to the Chewy MarketMedium API.
    pandas: For data manipulation and handling Excel files.
    datetime: For generating timestamps.
    json: For handling JSON data.

import os
import requests
import pandas as pd
from datetime import datetime
import json

deal_name = 'January Evergreen - 1.14.24 - 2.11.24 - LUMPSUM'
file_name = 'Evergreen billing Jan24.xlsx'
file_path = r'Z:\Systems & Process\Evergreen HC billing\billing_file\2024\Evergreen billing Jan24.xlsx'
report_folder = r'Z:\Systems & Process\Bulk Deal Creation\Mm_attachment_reports'
contract_pdf_folder = r'Z:\Systems & Process\Evergreen HC billing\Updated Evergreen H&W Agreements'

def create_all_sitewides(deal_name):
    url_all_sitewides = f"https://chewy.marketmedium.net/dealHeaders?org_type=vendor&deal_category=deal&deal_name={deal_name}"
    return url_all_sitewides

def authentication_call():
    payload = {}
    headers = {
        'Authorization': 'Basic a3NhbGF2ZXJyaWFyaWVkZWw6S3NfMDEwNjE5OTQhISEh',
        'Cookie': 'connect.sid=w02~s%3AevBnwDQdChhVQRveZyOtZ4y8ik-vxeYy.Z%2FadaA8I3UdbzOkNCiAcBXqyxStM4e9IaHURuy%2FBf8c'
    }
    authentication_url = "https://chewy.marketmedium.net/createSession?user_name=marketmedium@chewy.com&password=Welcome123"
    response = requests.request("POST", authentication_url, headers=headers, data=payload)
    r_dict = response.__dict__
    name = r_dict['cookies'].__dict__['_cookies']["chewy.marketmedium.net"]["/"]["connect.sid"].name
    value = r_dict['cookies'].__dict__['_cookies']["chewy.marketmedium.net"]["/"]["connect.sid"].value
    cookie = f"{name}={value}"
    return cookie

def deal_headercall(get_url, cookie):
    payload = {}
    headers = {
        'Authorization': 'Basic a3NhbGF2ZXJyaWFyaWVkZWw6S3NfMDEwNjE5OTQhISEh',
        'Cookie': f'{cookie}'
    }
    response_get = requests.request("GET", get_url, headers=headers, data=payload)
    dictionary = json.loads(response_get.text)
    result = pd.DataFrame.from_records(dictionary["data"])
    return result

def attachment_call_excel(url, file_name, file_path, cookie):
    payload = {}
    files = [
        ('Form', (f'{file_name}', open(f'{file_path}', 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
    ]
    headers = {'Cookie': f'{cookie}'}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)

def attachment_call_pdf(contract_url, file_name_pdf, file_path_pdf, cookie):
    payload = {}
    files = [
        ('Form', (f'{file_name_pdf}', open(f'{file_path_pdf}', 'rb'), 'application/pdf'))
    ]
    headers = {'Cookie': f'{cookie}'}
    response = requests.request("POST", contract_url, headers=headers, data=payload, files=files)

def contract_get_call(cookie, contract_info_df, get_url):
    success_uploaded_contracts = []
    not_uploaded_contracts = []

    for x in contract_info_df.index:
        vendor_number = contract_info_df["vendor_number"][x]
        vendor_name = contract_info_df["vendor_name"][x]
        file_name_pdf = contract_info_df["file_name"][x] + ".pdf"

        file_path_pdf = os.path.join(contract_pdf_folder, file_name_pdf)
        results_df = deal_headercall(get_url, cookie)

        if not results_df.empty:
            results_df = results_df.loc[results_df['beneficiary_name'] == vendor_name].copy(deep=True)
            results_df = results_df.reset_index(drop=True)

            if not results_df.empty:
                dealid = results_df["deal_header_id"][0]
                contract_url = f"https://chewy.marketmedium.net/attachment?object_type=deals&object_id={dealid}"

                attachment_call_pdf(contract_url, file_name_pdf, file_path_pdf, cookie)
                attachment_call_excel(contract_url, file_name, file_path, cookie)

                success_uploaded_contracts.append({
                    "vendor_name": vendor_name,
                    "contract_name": file_name_pdf,
                    "deal_number": dealid
                })
            else:
                not_uploaded_contracts.append({"vendor_name": vendor_name, "contract_name": file_name_pdf})
        else:
            not_uploaded_contracts.append({"vendor_name": vendor_name, "contract_name": file_name_pdf})

    return success_uploaded_contracts, not_uploaded_contracts

def save_csv_report(data, report_type):
    date_prefix = datetime.now().strftime("%m.%d.%Y")
    report_path = os.path.join(report_folder, f"{date_prefix}_{report_type}.csv")

    if not data.empty:
        if os.path.exists(report_path):
            existing_data = pd.read_csv(report_path)
            combined_data = pd.concat([existing_data, data], ignore_index=True)
            combined_data.drop_duplicates(subset=["vendor_name", "contract_name"], inplace=True)
            combined_data.to_csv(report_path, index=False)
        else:
            data.to_csv(report_path, index=False)

# Main execution
session_cookie = authentication_call()
url_all_sitewides = create_all_sitewides(deal_name)
contract_attach_info = pd.read_excel(file_path, sheet_name="Vendor_Contracts")

success_reports, failed_reports = contract_get_call(session_cookie, contract_attach_info, url_all_sitewides)

success_df = pd.DataFrame(success_reports)
failed_df = pd.DataFrame(failed_reports)

save_csv_report(success_df, "success")
save_csv_report(failed_df, "failed")

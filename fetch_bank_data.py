import sys
import argparse
import time
import shutil
import os
import StringIO
import pprint
import json
import datetime

import ofxclient
import ofxclient.config
import ofxclient.util
import ofxparse

current_bank_data_filename = "current_bank_data.ofx"
current_historic_data_filename = "current_bank_data.json"

def backup_filename(filename):
    dirname,basename = os.path.split(filename)
    filename,fileextension = os.path.splitext(basename)
    timestamp = time.strftime("%b-%d-%Y_%H%M%S",time.localtime())
    return os.path.join(dirname,filename + "_" + timestamp + fileextension)

def get_account_name(ofx_config,account_id):
    for account in ofx_config.accounts():
        if account.number == account_id:
            return account.description

    return "No Name"

def extract_accounts(accounts,ofx_config):
    retval = dict()

    for account in accounts:
        if hasattr(account.statement,'balance'):
            retval[account.account_id] = { 'balance': float(account.statement.balance),
                    'name':get_account_name(ofx_config,account.account_id)
                    }
    return retval

def save_ofx_data(ofx_data,work_dir):
    current_name = os.path.join(work_dir,current_bank_data_filename)
    if os.path.exists(current_name):
        backup_name = backup_filename(current_name)
        os.rename(current_name,backup_name)

    ofx_data.seek(0)
    with open(current_name,'wb') as current_ofx_file:
        current_ofx_file.write(ofx_data.getvalue())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch and Store Bank data using ofx')

    parser.add_argument("--work_dir",required=True,help="Directory in which to store serialized data")
    parser.add_argument("--ofx_config",required=True,help="ofxclient INI file")
    parser.add_argument("--test_ofx",help="Circumvent downloading ofxdata and use this ofx file instead")

    args = parser.parse_args()

    if not os.path.isdir(args.work_dir):
        os.makedirs(args.work_dir)

    ofx_config = ofxclient.config.OfxConfig(file_name=args.ofx_config)
    accounts = []
    for account in ofx_config.accounts():
        accounts.append(account)

    if not args.test_ofx:
        print "Downloading accounts ",accounts
        ofx_data = ofxclient.util.combined_download(accounts)
        print "Download completed"
        save_ofx_data(ofx_data,args.work_dir)
    else:
        with open(args.test_ofx,'rb') as test_ofx_file:
            ofx_data = StringIO.StringIO(test_ofx_file.read())


    historic_json_filename = os.path.join(args.work_dir,current_historic_data_filename)
    if os.path.exists(historic_json_filename):
        with open(historic_json_filename) as historic_json_file:
            historic_json = json.load(historic_json_file)
        backup_historic_name = backup_filename(historic_json_filename)
        os.rename(historic_json_filename,backup_historic_name)
    else:
        historic_json = []


    ofx = ofxparse.OfxParser.parse(ofx_data)

    historic_json.append({
        'datetime': datetime.datetime.now().isoformat(),
        'accounts': extract_accounts(ofx.accounts,ofx_config)
    })

    with open(historic_json_filename,'wb') as historic_json_file:
        json.dump(historic_json,historic_json_file)

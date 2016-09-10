import argparse
import ConfigParser
import pushover
import json
import dateutil
import dateutil.parser
import pprint

test_message = '''
CK: 1467.23 <font color="red">142.75</font> <font color="green">200.00</font>
MC: 1467.23 <font color="red">142.75</font> <font color="green">200.00</font>
US: 1467.23 <font color="red">142.75</font> <font color="green">200.00</font>
'''

def format_delta_with_color(delta):
    if delta >= 0:
        color = "green"
    else:
        color = "red"
    return '<font color="%s">%.2f</font>'%(color,delta)


def format_report_line(label,current_balance,last_balance,anchor_balance):
    return "%s: %.2f %s %s"%(label,current_balance,format_delta_with_color(current_balance - last_balance),format_delta_with_color(current_balance - anchor_balance))

def get_anchor_balance(json_banking_data,account,anchor_date):

    for bank_data in json_banking_data:
        bank_data_date = dateutil.parser.parse(bank_data['datetime']).date()
        if bank_data_date >= anchor_date:
            return float(bank_data['accounts'][account]['balance'])

    return float(json_banking_data[0]['accounts'][account]['balance'])

def main():
    message = ""

    parser = argparse.ArgumentParser(description='Update banking information')
    parser.add_argument('--config',required=True,help="Configuration file")
    args = parser.parse_args()

    config = ConfigParser.RawConfigParser()
    config.read(args.config)

    app_id = config.get('pushover','app_id')
    group_id = config.get('pushover','group_id')

    push = pushover.PushOver(app_id,group_id)

    anchor_date = dateutil.parser.parse(config.get('banking','anchor_date')).date()

    json_banking_data_filename = config.get('banking','current_json')
    with open(json_banking_data_filename) as json_banking_data_file:
        json_banking_data = json.load(json_banking_data_file)
    #pprint.pprint(json_banking_data)
    for account in config.get('banking','accounts').split(' '):
        label = config.get(account,'label')

        if config.has_option(account,'anchor_date'):
            anchor_date = dateutil.parser.parse(config.get(account,'anchor_date')).date()

        current_balance = float(json_banking_data[-1]['accounts'][account]['balance'])
        last_balance = float(json_banking_data[-2]['accounts'][account]['balance'])
        anchor_balance = get_anchor_balance(json_banking_data,account,anchor_date)
        message = message + format_report_line(label,current_balance,last_balance,anchor_balance) + "\n"

    push.sendmsg(message,title="Mr Banks Update",html=1)
    #print message

if __name__ == "__main__":
    main();

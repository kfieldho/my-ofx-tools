import argparse
import ConfigParser
import pushover
import json

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


def format_report_line(label,current_balance,last_balance,first_balance):
    return "%s: %.2f %s %s"%(label,current_balance,format_delta_with_color(current_balance - last_balance),format_delta_with_color(current_balance - first_balance))

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

    json_banking_data_filename = config.get('banking','current_json')
    with open(json_banking_data_filename) as json_banking_data_file:
        json_banking_data = json.load(json_banking_data_file)

    for account in config.get('banking','accounts').split(' '):
        label = config.get(account,'label')
        current_balance = float(json_banking_data[-1]['accounts'][account]['balance'])
        last_balance = float(json_banking_data[-2]['accounts'][account]['balance'])
        first_balance = float(json_banking_data[0]['accounts'][account]['balance'])
        message = message + format_report_line(label,current_balance,last_balance,first_balance) + "\n"

    push.sendmsg(message,title="Mr Banks Update",html=1)
    #print message

if __name__ == "__main__":
    main();

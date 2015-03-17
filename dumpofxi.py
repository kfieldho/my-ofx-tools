import ofxparse 
import pprint
import sys

#ofx = ofxparse.OfxParser.parse(file('combined_download.ofx'))
ofx = ofxparse.OfxParser.parse(file(sys.argv[1]))

#pprint.pprint(ofx.__dict__)

if len(ofx.accounts):
    for account in ofx.accounts:
        #print "%s: %d"%(account.account_id,account.statement.balance)
        pprint.pprint(account.__dict__)
        pprint.pprint(account.statement.__dict__)
        if 'positions' in account.statement.__dict__:
            for position in account.statement.positions:
                pprint.pprint(position.__dict__)


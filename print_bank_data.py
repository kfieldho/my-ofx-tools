import json
import pprint
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="Pretty Print JSON data")
    parser.add_argument("json_filename",help="Name of JSON filename to print")

    args = parser.parse_args()

    if os.path.exists(args.json_filename):
        with open(args.json_filename) as json_file:
            json_data = json.load(json_file)

            pprint.pprint(json_data)

if __name__ == "__main__":
    main()

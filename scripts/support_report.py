"""Offline, operator-only support counts. No web endpoint."""
import argparse
import json
from support.intelligence import summary, retention

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--app")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--purge-older-than", type=int, help="Explicitly purge old records")
    args = parser.parse_args()
    if args.purge_older_than is not None:
        print("deleted:", retention(args.db, args.purge_older_than))
    print(json.dumps(summary(args.db, args.app, args.days), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

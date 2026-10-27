"""Explicit local review export for all nine Drill image families. No DB/R2 calls."""
import argparse
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'variant_gen'))
from bank import load_workspace_bank
from config_store import ConfigStore
from conceptual_stock import load_stock
from drill_media_review import build_review,verify_review_files,write_review


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--seed',type=int,help='One variant per numerical family; omit to cover all 150 variants.')
    args=parser.parse_args()
    bank=load_workspace_bank(ROOT/'variant_gen/data/q0_bank.csv')
    configs=ConfigStore(ROOT/'variant_gen/configs')
    stocks=load_stock(ROOT/'variant_gen/data/conceptual_stock.json',bank)
    files=build_review(bank,configs,stocks,seed=args.seed)
    output=write_review(files,args.output)
    print(json.dumps({**verify_review_files(files),'output':str(output)},indent=2))


if __name__=='__main__':main()

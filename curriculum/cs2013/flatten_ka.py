import argparse
import json
import os
import pandas as pd


def parse_cmd_line():
    parser = argparse.ArgumentParser(prog="PROG")
    parser.add_argument(
        "--data_dir", nargs=1, help="directory for input and output files"
    )
    parser.add_argument(
        "in_file", nargs="+", help="input json file for a knowledge area"
    )
    parser.add_argument(
        "out_file", nargs="+", help="output csv file for the knowledge area"
    )
    args = parser.parse_args()
    return args


def convert_to_dataframe(ka_fn):
    with open(ka_fn, mode="rt") as f:
        ka = json.load(f)
    if not ka:
        raise ValueError("ka is empty")
    df = pd.DataFrame()
    row_list = []
    for ku in ka["units"]:
        for t in ku["topics"]:
            subtopic_list = [""]
            subtopic_list.extend(t["subtopics"])
            for st in subtopic_list:
                if t["tier"]:
                    tier = t["tier"]
                elif isinstance(ku["tiers"], list):
                    tier = ku["tiers"][0]["tier"]
                else:
                    tier = ku["tiers"]["tier"]
                row_list.append(
                    {
                        "KA": ka["short_ka"],
                        "Knowledge Area": ka["ka"],
                        "Knowledge Unit": ku["ku"],
                        "Tier": tier,
                        "Topic": t["topic"],
                        "Subtopic": st if st else t["topic"],
                    }
                )
    df = pd.DataFrame(row_list)
    return df


def main():
    data_dir = os.path.join("webknwlmap", "curriculum", "data")
    args = parse_cmd_line()
    if args.data_dir:
        data_dir = args.data_dir[0]
    ka_fn = os.path.join(data_dir, args.in_file[0])
    df = convert_to_dataframe(ka_fn)
    output_fn = os.path.join(data_dir, args.out_file[0])
    df.to_csv(output_fn, index=False)
    print("wrote to {}".format(output_fn))


if __name__ == "__main__":
    main()

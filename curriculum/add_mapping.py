import os
import numpy as np
import pandas as pd


def main():
    mapping_fn = os.path.join("webknwlmap", "curriculum", "data", "cs2013_ku_cwe.csv")
    cs2013_fn = os.path.join("webknwlmap", "curriculum", "data", "cs2013_web_final.csv")
    output_fn = os.path.join("webknwlmap", "curriculum", "data", "cs2013_web_final_cwe.csv")
    mapping_df = pd.read_csv(mapping_fn, dtype=str)
    cs2013_df = pd.read_csv(cs2013_fn, dtype=str)
    df = pd.merge(
        cs2013_df,
        mapping_df,
        left_on=["KA", "Knowledge Unit", "Subtopic"],
        right_on=["KA", "Knowledge Unit", "Topic"],
        how="left",
    )
    df = df.replace(np.nan, "")
    df.drop(columns=['Topic_y'], inplace=True)
    df.rename(columns={'Topic_x': 'Topic'}, inplace=True)
    df.to_csv(
        output_fn,
        index=False,
    )
    print("wrote to {}".format(output_fn))


if __name__ == "__main__":
    main()

import os
import pandas as pd

if __name__ == '__main__':
    file_list = ["cs2013_web_final_sf.csv",
        "cs2013_web_final_se.csv",
        "cs2013_web_final_pl.csv",
        "cs2013_web_final_ias.csv",
        "cs2013_web_final_sdf.csv"
    ]
    df_list = []
    for f in file_list:
        csv_f = os.path.join("webknwlmap", "curriculum", "data", f)
        df = pd.read_csv(csv_f)
        df_list.append(df)
    df = pd.concat(df_list)
    out_fn = os.path.join("webknwlmap", "curriculum", "data", "cs2013_web_final.csv")
    df.to_csv(out_fn, index=False)
    print('worte to {}'.format(out_fn))
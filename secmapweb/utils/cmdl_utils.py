import argparse
import os

import streamlit as st

MAPPING_DATA_DIR = os.path.join("data")
# TOPIC_TO_CWE_DATA_FN = "topic_cwe.csv"
TOPIC_TO_CWE_DATA_FN = "cs2013_web_final_cwe.csv"
CVE_CWE_DATA_FN = "cve_cwe.csv"
CWE_LIST_FN = "cwe_list.csv"


class RunSettings:
    def __init__(self, *, data_dir=None):
        self._data_dir = data_dir if data_dir else MAPPING_DATA_DIR
        self._topic_to_cwe_data_fn = TOPIC_TO_CWE_DATA_FN
        self._cve_cwe_data_fn = CVE_CWE_DATA_FN

    def get_topic_to_cwe_file(self):
        return os.path.join(self._data_dir, self._topic_to_cwe_data_fn)

    @property
    def topic_to_cwe_file(self):
        return self.get_topic_to_cwe_file()

    def get_cve_cwe_file(self):
        return os.path.join(self._data_dir, self._cve_cwe_data_fn)

    @property
    def cve_cwe_file(self):
        return self.get_cve_cwe_file()

    def get_cwe_list_file(self):
        return os.path.join(self._data_dir, CWE_LIST_FN)

    @property
    def cwe_list_file(self):
        return self.get_cwe_list_file()


def setup_parser(app_name):
    parser = argparse.ArgumentParser(
        prog=app_name, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--data_dir",
        type=str,
        default=MAPPING_DATA_DIR,
        help="Data directory for mapping data",
    )
    return parser


def get_run_settings(app_name):
    parser = setup_parser(app_name)
    args = parser.parse_args()
    if args.data_dir:
        st.session_state["data_dir"] = args.data_dir
        return RunSettings(data_dir=args.data_dir)
    elif "data_dir" in st.session_state:
        return RunSettings(data_dir=st.session_state["data_dir"])
    else:
        return RunSettings()

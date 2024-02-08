import streamlit as st
import loguru as logger
from utils.cmdl_utils import get_run_settings

# a simple about page to display the version of the app (0.0.1) and the goal of this app:
# This is a web application maps between software security topics (CWEs and CVEs) and CS curriculum topics. It serves two main goals:
# it allows instructors or learners understand what prerequisite material is needed to help teach/learn about certain 
# secure programming topics in terms of CWEs and CVEs, and
# it also helps them locate real world examples, such as CWEs and CVEs relevant to a course topic.
# printed on the page using html and styled with css

def main():
    st.markdown(
        """
        <style>
        .big-font {
            font-size:20px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <p class="big-font">
        This is a web application maps between software security topics (CWEs and CVEs) and CS curriculum topics. It serves two main goals:
        <ul>
        <li>it allows instructors or learners understand what prerequisite material is needed to help teach/learn about certain
        secure programming topics in terms of CWEs and CVEs, and</li>
        <li>it also helps them locate real world examples, such as CWEs and CVEs relevant to a course topic.</li>
        </ul>
        </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <p class="big-font">
        App Version: 0.0.1
        </p>
        """,
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()
from contextlib import contextmanager

import streamlit as st

from utils.github_json_store import StorageError


@contextmanager
def storage_action():
    try:
        yield
    except StorageError as exc:
        st.error(str(exc))
        st.stop()

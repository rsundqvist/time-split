import logging
from typing import Any

import pandas as pd
import streamlit as st

_LOGGER = logging.getLogger("time-split.streamlit")


def log_perf(message: str, df: pd.DataFrame, seconds: float, extra: dict[str, Any]) -> str:
    extra = extra | {
        "duration_ms": int(1000 * seconds),
        "size": df.size,
        "rows": len(df),
        "columns": len(df.columns),
        "remote_ip": get_remote_ip(),
    }
    message = message.format_map(extra)
    _LOGGER.info(message.replace("`", "") + f" | {extra=}", extra=extra)
    return message


class StreamlitLoggingHandler(logging.Handler):
    def emit(self, record):
        message = record.getMessage()

        if record.levelno >= logging.ERROR:
            st.error(message, icon="🚨")
        elif record.levelno >= logging.WARNING:
            st.warning(message, icon="⚠️")
        elif record.levelno >= logging.INFO:
            st.info(message, icon="ℹ️")
        else:
            st.code(record.levelname + ": " + record.getMessage())


@st.cache_data
def get_remote_ip() -> str:
    from streamlit.runtime import get_instance
    from streamlit.runtime.scriptrunner import get_script_run_ctx

    ctx = get_script_run_ctx()
    client = get_instance().get_client(ctx.session_id)
    assert client is not None
    return client.request.remote_ip

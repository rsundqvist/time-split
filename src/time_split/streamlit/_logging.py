import logging
from typing import Any

import pandas as pd
import streamlit as st

LOGGER = logging.getLogger("time_split.streamlit")


def log_perf(message: str, df: pd.DataFrame, seconds: float, **extra: Any) -> None:
    extra = extra | {
        "duration_ms": int(1000 * seconds),
        "size": df.size,
        "rows": len(df),
        "columns": len(df.columns),
    }
    LOGGER.info(message, extra=extra)


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

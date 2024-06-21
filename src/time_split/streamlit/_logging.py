import logging

import streamlit as st


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


def configure_logger(logger: logging.Logger, *, level: int = logging.INFO) -> None:
    logger.setLevel(level)
    logger.addHandler(StreamlitLoggingHandler())

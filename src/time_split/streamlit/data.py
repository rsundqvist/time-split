import pandas as pd
import streamlit as st


def sample_data(
    *,
    repeat: int = 2,
    start: str | None = None,
    end: str | None = "2019-05-11 20:30",
    freq: str = "h",
) -> pd.DataFrame:
    from pathlib import Path

    timeseries = pd.read_csv(Path(__file__).parent / "timeseries.csv", header=None)
    reverse_timeseries = timeseries.iloc[::-1]

    df = pd.concat([timeseries, reverse_timeseries] * repeat, ignore_index=True)
    df.columns = [f"Column {i}" for i in df]
    df["timestamp"] = pd.date_range(start, end, freq=freq, periods=len(df))

    return df


def load() -> pd.DataFrame:
    df: pd.DataFrame = sample_data()

    df = df.convert_dtypes(dtype_backend="pyarrow")

    rows = f"{len(df):_d}" if len(df) > 9999 else str(len(df))
    st.write(f"Source `sample.csv` returned {rows} rows and {len(df.columns)} columns.")

    return df


def select_index(df: pd.DataFrame) -> tuple[pd.DataFrame, tuple[pd.Timestamp, pd.Timestamp]]:
    index: None | int = None

    lower: pd.Index = df.columns.map(str.lower)
    for s in "date", "time", "datetime", "timestamp":
        try:
            index = lower.get_loc(s)
            break
        except KeyError:
            pass

    selection = st.selectbox("Choose index", options=df.columns, index=index)

    # df[selection] = df[selection].map(date.fromisoformat)
    # TypeError: Cannot compare Timestamp with datetime.date. Use ts == pd.Timestamp(date) or ts.date() == date instead.
    df[selection] = df[selection].map(pd.Timestamp)

    df = df.set_index(selection)

    st.write(f"Index column: `{selection!r}:{df.index.dtype}`")

    return df, (df.index.min(), df.index.max())


def select_columns(df: pd.DataFrame) -> pd.DataFrame:
    columns = df.columns.to_list()
    selection = st.multiselect("Columns", columns, columns)
    if not selection:
        selection = columns

    df = df[selection]

    types = (f"{col!r}: {dtype}" for col, dtype in df.dtypes.items())
    st.write(f"Chosen columns ({len(selection)}/{len(columns)}): `{', '.join(types)}`")
    return df

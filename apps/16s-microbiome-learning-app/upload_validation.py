"""Bounded CSV input for the public learning demo."""
import csv
import io
import re
import numpy as np
import pandas as pd

MAX_BYTES = 2 * 1024 * 1024
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_. -]{0,79}\Z")

def parse_uploads(metadata_bytes: bytes, counts_bytes: bytes):
    if any(not data or len(data) > MAX_BYTES for data in (metadata_bytes, counts_bytes)):
        raise ValueError("各CSVは空でない2 MiB以下のファイルにしてください。")
    try:
        texts = [data.decode("utf-8-sig") for data in (metadata_bytes, counts_bytes)]
        for text in texts:
            header = next(csv.reader(io.StringIO(text)))
            if len(header) > 501 or len(header) != len(set(header)):
                raise ValueError("列数が多すぎるか、列名が重複しています。")
        metadata = pd.read_csv(io.StringIO(texts[0]), nrows=101, dtype=str, keep_default_na=False)
        counts = pd.read_csv(io.StringIO(texts[1]), nrows=101, index_col=0)
    except (UnicodeError, csv.Error, pd.errors.ParserError, pd.errors.EmptyDataError, StopIteration) as error:
        raise ValueError("UTF-8の正しいCSVを指定してください。") from error
    if set(metadata.columns) != {"SampleID", "Group"}:
        raise ValueError("Metadataの列はSampleIDとGroupだけにしてください。")
    if not (4 <= len(metadata) <= 100 and 4 <= len(counts) <= 100 and 2 <= len(counts.columns) <= 500):
        raise ValueError("4〜100検体、2〜500 ASVに制限されています。")
    if metadata["SampleID"].duplicated().any() or not counts.index.is_unique:
        raise ValueError("SampleIDは一意にしてください。")
    counts.index = counts.index.astype(str)
    identifiers = [*metadata["SampleID"], *metadata["Group"], *counts.index, *counts.columns]
    if any(not isinstance(value, str) or not IDENTIFIER.fullmatch(value) for value in identifiers):
        raise ValueError("IDとGroupには許可された英数字・空白・_・.・-だけを使用してください。")
    if set(metadata["SampleID"]) != set(counts.index):
        raise ValueError("両CSVのSampleIDを一致させてください。")
    groups = metadata["Group"].value_counts()
    if len(groups) != 2 or (groups < 2).any():
        raise ValueError("2群それぞれに2検体以上が必要です。")
    try:
        values = counts.to_numpy(dtype=float)
    except (ValueError, TypeError) as error:
        raise ValueError("カウントは数値にしてください。") from error
    if not np.isfinite(values).all() or (values < 0).any() or (values > 1_000_000_000).any() or (values != np.floor(values)).any():
        raise ValueError("カウントは0〜10億の有限な整数にしてください。")
    if (values.sum(axis=1) <= 0).any():
        raise ValueError("各検体に正のカウントが必要です。")
    return metadata, pd.DataFrame(values, index=counts.index, columns=counts.columns)

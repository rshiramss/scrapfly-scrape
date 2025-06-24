import json
from pathlib import Path


def save_jsonl(records, output_dir, prefix="chunk", chunk_size=100000):
    """Save list of records to JSONL files.

    Parameters
    ----------
    records : list
        List of dictionaries to save.
    output_dir : str or Path
        Directory path where JSONL files will be created.
    prefix : str, optional
        File name prefix for chunk files, by default "chunk".
    chunk_size : int, optional
        Maximum number of records per chunk file, by default 100000.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    total = len(records)
    if total == 0:
        return

    if total > chunk_size:
        for index in range(0, total, chunk_size):
            chunk_records = records[index : index + chunk_size]
            chunk_path = output_dir / f"{prefix}_{index // chunk_size + 1:03d}.jsonl"
            with open(chunk_path, "w", encoding="utf-8") as f:
                for record in chunk_records:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
    else:
        chunk_path = output_dir / f"{prefix}_001.jsonl"
        with open(chunk_path, "w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

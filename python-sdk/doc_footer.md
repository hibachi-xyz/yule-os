
# Development

```sh
cd yule
python3 -m venv python-sdk

# Run tests
./bin/pytest -v -s

# Run a specific test
./bin/pytest -s -v test_hibachi.py::test_place_market_order
```

## Generate Docs

Docs are auto generated using https://niklasrosenstein.github.io/pydoc-markdown/

Update `doc_header.md` and `doc_footer.md`

```sh
cd python-sdk
./bin/pip install pydoc_markdown --force
./bin/python docs.py
# updates README.md
```
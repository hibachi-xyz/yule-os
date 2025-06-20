
# Development

```sh
cd yule
python3 -m venv python-sdk

# Run tests
./bin/pytest -v -s
```

## Generate Docs

Docs are auto generated using https://niklasrosenstein.github.io/pydoc-markdown/

Update `doc_header.md` and `doc_footer.md`

```sh
./bin/python docs.py
# updates README.md
```
# Unit Tests

## Create a file for enviorment variables

First create a `.env` file here with

```ini
API_BASE_URL=http://127.0.0.1:8000
TIMEOUT=10
DISTRITOS_CLAVES=["001","002","003"]
```

## Running the tests

To run one test, for example `test_distritos.py`, run:

```bash
python3 -m unittest tests.test_autoridades
```

To run all tests, run:

```bash
python3 -m unittest discover
```

# InvenioRDM E2E tests

## Running locally

### Initial setup

> Documentation based on: [Installation | Playwright Python](https://playwright.dev/python/docs/intro)

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
source .venv/bin/activate[.csh|.fish]

# Install the required libraries
pip install -r requirements.txt

# Install the required browsers
playwright install
```

Create a `.env` file and fill in the following content:

```
E2E_USER1_EMAIL=...
E2E_USER1_PASSWORD=...
E2E_USER2_EMAIL=...
E2E_USER2_PASSWORD=...
```

### Running/debugging tests

> Documentation based on: [Running and debugging tests | Playwright Python](https://playwright.dev/python/docs/running-tests)

Run tests with the following command:

```bash
pytest
```

> [!TIP]
> Each failing test has a _trace_, _screenshots_ and _videos_ located in the `test-results/` directory.
> The trace can be analyzed by running `playwright show-trace test-results/<...>/trace.zip`

Tests can also be executed with a step by step debugger with the following command:

```bash
PWDEBUG=1 pytest -s
```

### Writing/modifying tests

Documentation based on: [Generating tests | Playwright Python](https://playwright.dev/python/docs/codegen-intro)

To get help writing tests, try the interactive test generation:

```bash
playwright codegen --viewport-size "1600, 1000" inveniordm.web.cern.ch
```

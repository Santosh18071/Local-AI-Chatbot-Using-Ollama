# Verification — 22 October 2026

## Checks completed

- Python 3.12.14, Windows x86-64, using the bundled Python runtime because the
  Windows Python launcher reported no registered Python installations.
- Official Ollama Python client 0.6.3 installed successfully in an isolated service
  test environment, with HTTPX 0.28.1 and Pydantic 2.14.1.
- **10 service tests passed**, using the real SDK response types and a mocked client.
  They check successful replies, system instruction and history, configured model,
  loopback client settings, connection errors, missing model and server errors,
  malformed replies, timeouts, sanitized exceptions, invalid input, and cloud names.
- **4 interface tests passed** using Streamlit AppTest: conversation and follow-up
  history, clear, error and retry without duplication, discard, empty input, and
  connection-check feedback. **All 14 tests passed in 1.123 seconds** on the final run.
- Streamlit 1.66.1 was installed successfully after selecting PyArrow 17.0.0, an
  allowed supporting dependency, to work around stalled newer-wheel downloads.
  The direct dependencies remain the two libraries in requirements.txt.
- `pip check` reported **No broken requirements found**. Application imports passed.
- A real request to the local Ollama address produced the friendly connection
  failure message. No internal exception details were displayed by the service.
- Python syntax compilation passed for the application, configuration, service,
  and tests.
- Static review completed; the UI style detector reported no findings. These
  checks alone do not establish accessibility compliance.
- The actual Streamlit server started at `127.0.0.1:8501`. Browser inspection
  confirmed the welcome screen, real connection-error rendering, and distinct
  user/assistant message surfaces. Responsive checks at 1280 px and 390 px widths
  found no horizontal overflow. Mobile heading spacing and small-text contrast
  were corrected and confirmed. Desktop/mobile previews were saved separately.
- Independent source and screenshot review found no blocking finish issues.

## Limits of verification

- Initial PyArrow downloads timed out or stalled. Installation completed using
  the older, compatible PyArrow 17.0.0 Windows wheel. The Windows README command
  includes this tested workaround; the newest supporting-wheel combination was not tested.
- Ollama's executable was not found on PATH or in its usual per-user installation
  folder. Nothing was accepting connections at `127.0.0.1:11434`.
- No model was downloaded. Actual model answers, speed, memory use, and hardware
  compatibility were **not tested**. The hardware inventory query was denied.
- Windows was the available host. macOS and Linux setup instructions were checked
  against official documentation but were not executed on those operating systems.

## Reproduce the completed tests

From the project folder, after installing `requirements.txt`, run:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_ollama_service.py -v
.\.venv\Scripts\python.exe -m compileall -q app.py config.py ollama_service.py tests
```

To run all 14 included tests (including the four UI cases), use:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The build's test environments are under `work/.venv` and `work/service-venv`,
outside the delivered project. The README creates a fresh `.venv` inside the
project so the setup is portable and independent of Codex's bundled runtime.

See README.md for macOS/Linux commands and the manual real-model check.

# AGENTS.md

Guidance for AI assistants working in this repository.

## What this is

unittest-parallel is a parallel unit test runner for Python with coverage support, published to PyPI as `unittest-parallel`. Console entry point: `unittest_parallel.main:main`.

The implementation is one module: `src/unittest_parallel/main.py`. Tests are `src/tests/test_main.py`. Runtime dependency: `coverage >= 5.1`. Supported Python: 3.11–3.15.

## Build system

Development uses [python-build](https://github.com/craigahobbs/python-build#readme). Drive all normal work through `make` — do not invent ad-hoc venv or tool invocations.

The thin `Makefile` downloads (or copies from `../python-build` via `PYTHON_BUILD_DIR`) `Makefile.base` and `pylintrc` on first run. Those files are gitignored; `make clean` deletes them. Do not commit or hand-edit them. Virtualenvs live under `build/venv/`. Cold `make` is by design (network on first run unless the sibling python-build tree is present).

This repo has no Sphinx docs (`SPHINX_DOC` is unset), so `make doc` is a no-op. `make commit` still depends on it.

### Day-to-day targets

| Target | When to use |
|--------|-------------|
| `make test` | After code/test changes |
| `make lint` | pylint on `src/` (docstring warnings disabled in this Makefile) |
| `make cover` | Before finishing; **100% branch coverage, fail-under 100** |
| **`make commit`** | **Before every commit** (`test` + `lint` + `doc` + `cover`) |
| `make clean` | Drop `build/`, downloaded `Makefile.base`/`pylintrc` |
| `make superclean` | `clean` plus container images (when using Docker/Podman) |

Never lower the coverage gate, skip `cover`, or leave untested branches. If coverage fails, add tests or remove dead code. `# pragma: no cover` is only for version/platform-dependent branches (argparse `color` on 3.14+, skipped-test bodies, and the `sys.version_info` golden-output arms — see Conventions).

Run a subset (also works with `make cover`):

```sh
make test TEST=tests.test_main.TestMain.test_success
make test TEST=tests.test_main
```

`TEST=` is a `unittest` module/class/method id passed to `python -m unittest` (the editable install puts `src/` on `sys.path`). Default `make test` / `make cover` (no `TEST`) uses `unittest discover -t src/ -s src/tests/`. Do not use discover-relative ids such as `test_main.TestMain.test_success`.

Default `make` uses the system Python. Multi-version:

```sh
make commit USE_DOCKER=1    # or USE_PODMAN=1
```

### Explicit user request only

Do **not** run these unless the user asks: `make changelog` (rewrites `CHANGELOG.md`), `make publish` (PyPI; runs `commit` first), `make gh-pages`. Confirm before publish.

Version lives in `pyproject.toml`. Changelog is generated from git history via `simple-git-changelog`.

## Architecture

Flow in `main()`:

1. Parse args (`argparse`; `color=False` on Python 3.14+).
2. Discover tests with `unittest.TestLoader.discover` **under `_coverage`**, so import-time code is measured.
3. Flatten the discovered suite into parallelizable sub-suites by `--level`: `_iter_module_suites` (default), `_iter_class_suites`, or `_iter_test_cases`.
4. Cap worker count at the number of sub-suites (and at least 1).
5. Run sub-suites:
   - Default: `multiprocessing.get_context(method='spawn').Pool` + `Manager().Event()` for failfast. `pool.map` always uses `chunksize=1`. `--disable-process-pooling` sets `maxtasksperchild=1`.
   - `--thread`: `ThreadPoolExecutor` + `threading.Event()`. Coverage is managed once in the parent (`coverage.py`'s collector is one-per-process). `-b` is ignored (unittest buffering is process-global).
6. Aggregate result tuples, print errors/failures from the parent, report, combine coverage files, optional HTML/XML/`--coverage-fail-under`.

Worker entry points: `_run_tests_process` (process pool; wraps `_coverage` then `_run_tests_thread`) and `_run_tests_thread` (actual `unittest` run).

### Constraints that shape the code

- **Spawn pickling.** Everything sent to/from process workers must pickle. Workers return `(testsRun, error_texts, failure_texts, skipped_count, expected_failure_count, unexpected_success_texts)`. `_run_tests_error` turns each unittest error/failure into a printable string (description + unittest's already-stringified traceback); unexpected successes use the same shape with body `UNEXPECTED SUCCESS`. `skipped_count` and `expected_failure_count` are `len(...)` counts. Failfast is a spawn-context `Manager.Event()` passed through `functools.partial` (not an initializer).
- **Coverage is per-process.** `_coverage` writes each process's data to a randomly named file in a shared temp dir; the parent `cov.combine`s them. The runner's own file is omitted from measurement. With `--thread`, one coverage context wraps the whole pool.
- **`ParallelTextTestResult` writes directly to `sys.stderr`** (rebinding the runner stream) so per-test output interleaves live across workers, and `printErrors` is a no-op — the parent prints aggregated error text after all workers finish.
- **`--runner` / `--result`** load `<module>.<class>` via importlib. When either is set, the parent skips the default summary report and does not capture the runner stream to a `StringIO`.

Tests mock `multiprocessing.get_context` (`MockMultiprocessingContext` / `MockMultiprocessingPool`) and `ThreadPoolExecutor` (`MockThreadPoolExecutor`) so worker code runs in-process — deterministic and visible to coverage. New paths in `main.py` need tests.

CLI flags and user-facing behavior are documented in `README.md`; keep that usage block in sync if you add or rename options.

## Conventions

- 4-space indent, max line length **140**, single quotes.
- MIT license header plus GitHub license URL at the top of every source file (`src/unittest_parallel/__main__.py` has a module docstring; this Makefile disables pylint missing-docstring checks).
- `unittest` tests. Golden stderr is compared via `TestMain.assert_output`, which normalizes timing (`<SEC>s`) and `File "...", line N`. It only strips pure-caret lines (`^`); it does **not** strip 3.13+ traceback emphasis (`~~~~~~~~~^^`). Description strings use the 3.11+ form (`FailureTestCase.mock_2`). When a golden includes an assertion traceback, split on `sys.version_info < (3, 13)` (`# pragma: no cover` on each arm) for the caret line. Do not add `< (3, 11)` arms.
- No new runtime dependencies without a strong reason. Do not add a Sphinx doc tree unless asked.
- Prefer small, local edits in `main.py`. Do not reintroduce `ProcessPoolExecutor` / worker initializers unless there is a concrete spawn-pickle reason; the process/thread runners were simplified on purpose (v1.8.x).

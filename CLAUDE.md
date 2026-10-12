# CLAUDE.md

Guidance for AI assistants working in this repository.

## What this is

unittest-parallel is a parallel unit test runner for Python with coverage support, published to PyPI as `unittest-parallel`. Console entry point: `unittest_parallel.main:main`.

The implementation is one module: `src/unittest_parallel/main.py`. Tests are `src/tests/test_main.py`.

## python-build

This is a [python-build](https://github.com/craigahobbs/python-build#readme) package. Read the python-build skill before running tests, lint, coverage, or changing the Makefile: [`../python-build/SKILL.md`](../python-build/SKILL.md) if that file exists, otherwise [https://raw.githubusercontent.com/craigahobbs/python-build/main/SKILL.md](https://raw.githubusercontent.com/craigahobbs/python-build/main/SKILL.md).

Local Makefile overrides:

- `PYLINT_ARGS` — missing docstring checks disabled
- no `SPHINX_DOC` — `make doc` is a no-op

`# pragma: no cover` is only for lines that can't run under the gate: version-dependent branches (argparse `color` on 3.14+, the `sys.version_info` golden-output arms — see Conventions), skipped-test bodies, and the `__main__.py` guard.

The Makefile leaves `UNITTEST_PARALLEL` unset, so `make test` / `make cover` use plain `unittest` / `coverage run` — the runner omits its own `main.py` from `--coverage` measurement, so this repo cannot self-measure with it.

## Architecture

Flow in `main()`:

1. Parse args (`argparse`; `color=False` on Python 3.14+). `--coverage-branch` implies `--coverage`; `-j 0` (or negative) means `cpu_count()`; `--runner` / `--result` classes are imported.
2. Discover tests with `unittest.TestLoader.discover` **under `_coverage`**, so import-time code is measured.
3. Flatten the discovered suite into parallelizable sub-suites by `--level`: `_iter_module_suites` (default), `_iter_class_suites`, or `_iter_test_cases`.
4. Cap worker count at the number of sub-suites (and at least 1).
5. Run sub-suites:
   - Default: `multiprocessing.get_context(method='spawn').Pool`. Failfast is a spawn `Event()` installed in each worker by `Pool(initializer=_init_worker, initargs=(event,))` (not a `Manager`, and not pickled on every `map` task). `pool.map` always uses `chunksize=1`. `--disable-process-pooling` sets `maxtasksperchild=1`.
   - `--thread`: `ThreadPoolExecutor` + `threading.Event()`. Coverage is managed once in the parent (`coverage.py`'s collector is one-per-process). `-b` / `--buffer` with `--thread` is a `parser.error` (exit 2); unittest buffering is process-global.
6. Aggregate result tuples. Print error/failure/unexpected-success text (skipped with `--result`), then the `Ran N tests` / `OK|FAILED` summary (skipped with `--runner` / `--result`). With coverage, always combine and report (even on test failure), then optional HTML/XML; `--coverage-fail-under` exits 2. Otherwise exit `min(255, errors + failures + unexpected successes)`.

Worker entry points: `_run_tests_process` (process pool; wraps `_coverage` then `_run_tests_thread`) and `_run_tests_thread` (actual `unittest` run).

### Constraints that shape the code

- **Spawn pickling.** Everything sent to/from process workers must pickle. Workers return `(testsRun, error_texts, failure_texts, skipped_count, expected_failure_count, unexpected_success_texts)`. `_run_tests_error` turns each unittest error/failure into a printable string (description + unittest's already-stringified traceback); unexpected successes use the same shape with body `UNEXPECTED SUCCESS`. `skipped_count` and `expected_failure_count` are `len(...)` counts. Failfast is a spawn `Event()` inherited via `Pool` initializer into `_WORKER_FAILFAST_EVENT` (a raw `Event` cannot be a `map` argument). Unstarted suites skip when the Event is set (the early return `[0, [], [], 0, 0, []]` must keep the same 6-slot shape); `ParallelTextTestResult` also checks it in `startTest`/`stopTest` so an in-flight suite stops after the current test. A custom `--result` class gets no Event, so only unstarted suites skip.
- **Coverage is per-process.** `_coverage` writes each process's data to a randomly named file in a shared temp dir; the parent `cov.combine`s them. The runner's own file is omitted from measurement. With `--thread`, one coverage context wraps the whole pool.
- **`ParallelTextTestResult` writes directly to `sys.stderr`** (rebinding the runner stream) so per-test output interleaves live across workers, and `printErrors` is a no-op — the parent prints aggregated error text after all workers finish.
- **`--runner` / `--result`** load `<module>.<class>` via importlib. A spec with no `.` is `parser.error` (exit 2); an unknown module or class raises a plain `ImportError` / `AttributeError` (tests assert this). When either is set, the parent skips the default summary and does not capture the runner stream to a `StringIO`. When `--result` is set, the parent also skips reprinting errors/failures (the result class owns `printErrors`).

Tests patch `multiprocessing.get_context` (`MockMultiprocessingContext` / `MockMultiprocessingPool` / `MockMultiprocessingManagerEvent` — a legacy name; no `Manager` is used) and `unittest_parallel.main.ThreadPoolExecutor` (`MockThreadPoolExecutor`; patch it there, not in `concurrent.futures`) so worker code runs in-process — deterministic and visible to coverage. The mock `Pool` calls `initializer(*initargs)` so `_WORKER_FAILFAST_EVENT` is set. Do not use a real spawn `Pool` in tests: Pool workers are daemonic, so nested spawn fails if the suite is run under unittest-parallel. `test_thread_coverage` uses a real single-thread executor to cover the parent `--thread --coverage` wrap. Mock test methods are named `mock_*` so discovery skips them. New paths in `main.py` need tests.

CLI flags and user-facing behavior are documented in `README.md`; keep the usage block and the behavior sections ("Process and Thread Pools", "Custom Runner and Result") in sync when changing options or behavior.

## Conventions

- 4-space indent, max line length **140**, single quotes.
- MIT license header plus GitHub license URL at the top of every non-empty source file (the `__init__.py` files are empty). Docstrings are optional (the Makefile disables pylint missing-docstring checks).
- `unittest` tests. Golden stderr is compared via `TestMain.assert_output`, which normalizes timing (`<SEC>s`) and `File "...", line N`. It only strips pure-caret lines (`^`); it does **not** strip 3.13+ traceback emphasis (`~~~~~~~~~^^`). Description strings use the 3.11+ form (`FailureTestCase.mock_2`). When a golden includes an assertion traceback, split on `sys.version_info < (3, 13)` (`# pragma: no cover` on each arm) for the caret line. Do not add `< (3, 11)` arms.
- No new runtime dependencies without a strong reason.
- Prefer small, local edits in `main.py`. Do not reintroduce `ProcessPoolExecutor`. Failfast uses `Pool(initializer=_init_worker)` because a raw spawn `Event` cannot be a `map` argument.

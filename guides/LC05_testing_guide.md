# LC5 follow-along guide — Testing numerical power system code

*EG2140 · Lecturecise 5 hands-on, ~45 min. Work in your toolbox repo — by now it contains the loader (Lab 1) and the refactored screener (Lab 2), which is exactly what we test.*

## Part A — What a test proves (10 min)

You already have tests. Run them and read them:

```bash
pytest -q
pytest -v tests/test_loader.py     # -v: see each test's name
```

A test proves one narrow thing: *this assertion held, on this input, this time.* It does not prove the code is correct — it proves the code has not changed in a way this assertion notices. That is exactly what makes tests valuable when someone else (a lab partner, an AI agent) changes your code: the suite is your tripwire.

Three anatomy rules, visible in `tests/test_loader.py`: one idea per test; a name that states the idea (`test_power_flow_converges` reads as a sentence); assertions with messages where failure would otherwise be cryptic — `test_network_sizes` carries one (`"expected 52 buses, got ..."`); a bare `assert` next to it shows what you get without: just `52 != 51`.

## Part B — Numerical code needs tolerances (10 min)

Add this test to `tests/test_loader.py` and run it (the imports it needs — `load_svedala`, `run_power_flow` — are already at the top of that file; if you start a new test file instead, import them yourself):

```python
def test_losses_are_small_but_positive():
    net = run_power_flow(load_svedala())
    losses = net.res_line.pl_mw.sum() + net.res_trafo.pl_mw.sum()
    assert 0 < losses < 0.05 * net.res_load.p_mw.sum()
```

Note what it does **not** do: assert `losses == 302.7554`. Floating point, solver versions and platform differences make exact equality a lie waiting to happen. The patterns for numerical assertions:

- **Bounds with meaning**: losses positive and below 5% of load (physics, not decimals)
- **`pytest.approx`** when you do have a reference value: `assert total == pytest.approx(10981, abs=10)`
- **Conservation laws as tests**: generation = load + losses is a one-line assertion your network can never be allowed to break

## Part C — Fixtures and parametrisation (15 min)

Loading Svedala takes seconds; doing it in every test is waste — and your Lab 2 `tests/test_screener.py` almost certainly screens the network once per test. The cure is a **fixture**. Add this to your `tests/test_screener.py` (plus `import pytest` at the top if it is not there), then refactor your screener tests to take `results` as an argument instead of each computing its own:

```python
@pytest.fixture(scope="module")
def results():
    return screen_n1(load_svedala())
```

Every test taking `results` as an argument shares one computed instance — `scope="module"` means it is built once for the whole file. (The lecture's fixture had no `scope=` — that default rebuilds the value for every test, the safe choice when tests might change it; `module` is the right trade here because screening is slow and every test only *reads* the result.) Run `pytest -v tests/test_screener.py`: same tests, one screening run instead of several. Now parametrisation — one test body, many cases:

```python
@pytest.mark.parametrize("scaling", [0.8, 1.0, 1.05])
def test_power_flow_converges_across_loadings(scaling):
    net = load_svedala()
    net.load.scaling = scaling
    assert run_power_flow(net).converged
```

Run `pytest -v` and watch it appear as three named tests (`[0.8]`, `[1.0]`, `[1.05]`). Parametrisation is how you test *behaviour across a range* instead of one lucky point.

## Part D — Edge cases: where the bugs live (10 min)

The happy path rarely breaks. Test the edges — for our screener the edges are physical:

- **The stressed case**: at what scaling does `run_power_flow` still converge? Find the edge now — raise `net.load.scaling` step by step until `run_power_flow` raises. It comes sooner than you might guess: Part C's 1.05 already sits close to it. Write the test that pins your answer.
- **The empty case**: what *should* `screen_n1` return for a network where every line is already out of service? Decide, then encode the decision as a test. (Deciding is the point — the test forces the design question.)
- **The failure path**: `run_power_flow` promises a `RuntimeError` on non-convergence — Lab 1 had you write that promise into `src/svedala_toolbox/loader.py`, and the test holds it to it: `with pytest.raises(RuntimeError): ...` on a hopeless case (`net.load.scaling = 10`). If this test fails with pandapower's own exception instead, your Lab 1 code lets it escape unwrapped — fix the loader, not the test.
- **The invariant after a contingency**: the screener takes elements out of service and must put them back. `net.line.in_service` should be identical before and after a screening run, whatever happened in between — including when a case failed. That is a one-line test, and it catches the single most common screener bug.

The failure-path test is the one that matters most for Period 2: agent-written code habitually *swallows* failure. Your tests are the leash that notices.

## Self-check

1. `pytest -q` green, including your Part B and Part C additions
2. You can explain why `losses == 302.7554` is a bad assertion and what to write instead
3. Tomorrow's lab inverts everything: the bug exists first, and the test's job is to catch it

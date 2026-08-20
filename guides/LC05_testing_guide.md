# LC5 follow-along guide — Testing numerical power system code

*EG2140 · Lecturecise 5 hands-on, ~45 min. Work in your toolbox repo — by now it contains the loader (Lab 1) and the refactored screener (Lab 2), which is exactly what we test.*

## Part A — What a test proves (10 min)

You already have tests. Run them and read them:

```bash
pytest -q
pytest -q -v tests/test_loader.py     # -v: see each test's name
```

A test proves one narrow thing: *this assertion held, on this input, this time.* It does not prove the code is correct — it proves the code has not changed in a way this assertion notices. That is exactly what makes tests valuable when someone else (a lab partner, an AI agent) changes your code: the suite is your tripwire.

Three anatomy rules, visible in `test_loader.py`: one idea per test; a name that states the idea (`test_network_restored_after_screening` reads as a sentence); assertions with messages where failure would otherwise be cryptic.

## Part B — Numerical code needs tolerances (10 min)

Add this test and run it:

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

Loading Svedala takes seconds; doing it in every test is waste. `tests/test_screener.py` already shows the cure:

```python
@pytest.fixture(scope="module")
def results():
    return screen_n1(load_svedala())
```

Every test taking `results` as an argument shares one computed instance. Now parametrisation — one test body, many cases:

```python
@pytest.mark.parametrize("scaling", [0.8, 1.0, 1.05])
def test_power_flow_converges_across_loadings(scaling):
    net = load_svedala()
    net.load.scaling = scaling
    assert run_power_flow(net).converged
```

Run `pytest -q -v` and watch it appear as three tests. Parametrisation is how you test *behaviour across a range* instead of one lucky point.

## Part D — Edge cases: where the bugs live (10 min)

The happy path rarely breaks. Test the edges — for our screener the edges are physical:

- **The stressed case**: at what scaling does `run_power_flow` still converge? Write the test that pins the answer (you found the number in Lab 1's extension).
- **The empty case**: what *should* `screen_n1` return for a network where every line is already out of service? Decide, then encode the decision as a test. (Deciding is the point — the test forces the design question.)
- **The failure path**: `run_power_flow` promises a `RuntimeError` on non-convergence — the promise is in its docstring in `src/svedala_toolbox/loader.py`, and the test holds it to it: `with pytest.raises(RuntimeError): ...` on a hopeless case (`net.load.scaling = 10`).
- **The invariant after a contingency**: the screener takes elements out of service and must put them back. `net.line.in_service` should be identical before and after a screening run, whatever happened in between — including when a case failed. That is a one-line test, and it catches the single most common screener bug.

The failure-path test is the one that matters most for Period 2: agent-written code habitually *swallows* failure. Your tests are the leash that notices.

## Self-check

1. `pytest -q` green, including your Part B and Part C additions
2. You can explain why `losses == 302.7554` is a bad assertion and what to write instead
3. Tomorrow's lab inverts everything: the bug exists first, and the test's job is to catch it

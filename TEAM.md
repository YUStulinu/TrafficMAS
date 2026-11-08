# Team workflow

TrafficMAS+ is built by four people. Each of them owns one part of the code, works on a
branch of their own and changes only the files of their part. The rules are in
[.github/team.yml](.github/team.yml); CI enforces them.

| Part | Member | Role | Branch | Owns |
|---|---|---|---|---|
| 1 | IANCOVICI Teodor-Gabriel | Simulation Core & Network Architect | `part1-iancovici` | `trafficmas/sim/`, `trafficmas/network/`, `trafficmas/bus/`, `trafficmas/config.py`, `data/`, `scenarios/` (except the two below), `scripts/fetch_osm.py`, `tests/test_core.py`, `tests/test_network.py`, `tests/test_bus.py` |
| 2 | PRODAN Constantin-Iustin | Intersection Control & Negotiation | `part2-prodan` | `trafficmas/agents/intersection.py`, `trafficmas/agents/coordinator.py`, `trafficmas/control/`, `tests/test_control.py` |
| 3 | GHEORGHEVICI Mihai | Vehicles, Routing & Emergency | `part3-gheorghevici` | `trafficmas/agents/vehicle.py`, `trafficmas/agents/emergency.py`, `trafficmas/routing/`, `scenarios/grid_emergency.yaml`, `scenarios/grid_incident.yaml`, `tests/test_routing.py`, `tests/test_emergency.py` |
| 4 | DOBRA Robert-Cristian | Evaluation, Visualization & Experiments | `part4-dobra` | `trafficmas/metrics/`, `trafficmas/viz/`, `trafficmas/experiments/`, `trafficmas/cli.py`, `experiments/`, `results/`, `docs/`, `scripts/run_all_experiments.sh`, `scripts/plot_queues.py`, `tests/test_metrics.py` |

Two exceptions:
- Part 2 may also edit part 3, at the request of its owner.
- Files that belong to no part are **shared**: the interfaces in `trafficmas/contracts.py`, packaging, CI, the README, and the end-to-end tests (`tests/test_simulation.py`, `tests/test_invariants.py`). Only the maintainer (part 2) changes them. If you need a change there, for example a new field in a message, ask for it in an issue or a pull request comment.

To check who owns a file:

```bash
python scripts/check_ownership.py --owner trafficmas/routing/router.py
```

## Working on your part

```bash
git clone https://github.com/YUStulinu/TrafficMAS.git
cd TrafficMAS
git switch part3-gheorghevici          # your branch
python -m venv .venv
.venv/Scripts/python -m pip install -e .[dev]     # Linux/macOS: .venv/bin/python
```

Then change your files and commit. Before every push, check your work:

```bash
.venv/Scripts/python -m pytest -q
.venv/Scripts/python scripts/check_ownership.py part3-gheorghevici
git push
```

Every push to your branch runs the tests and the ownership check on GitHub (the *Actions* tab). A red ownership check lists the files that belong to someone else; undo those changes with `git restore --source origin/main -- <file>` and commit again.

## Getting your work into `main`

`main` always holds a working version of the whole project.

1. Open a pull request from your branch into `main`.
2. CI must be green: tests, lint and ownership.
3. A reviewer approves it: the owner of the changed files or the maintainer (GitHub does not let anyone approve their own pull request). GitHub asks them automatically through [.github/CODEOWNERS](.github/CODEOWNERS).
4. Merge it.

To get the others' latest work into your branch:

```bash
git fetch origin
git merge origin/main
```

## Keeping the project working

- Do not change the interfaces in `trafficmas/contracts.py` on your own: the other parts depend on them.
- Keep the tests of your part green, and add tests for what you add.
- If a change of yours alters the results, re-run the experiments (`bash scripts/run_all_experiments.sh`). The README numbers come from `results/` (part 4).

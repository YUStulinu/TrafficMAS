"""The ownership map in .github/team.yml stays consistent with the repository (shared)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from check_ownership import TEAM, editable_by, owner  # noqa: E402


def test_every_owned_path_exists():
    for part, cfg in TEAM["parts"].items():
        for path in cfg["paths"]:
            assert (ROOT / path).exists(), f"{part}: {path} does not exist"


def test_most_specific_path_wins():
    assert owner("scenarios/grid_light.yaml") == "part1"
    assert owner("scenarios/grid_emergency.yaml") == "part3"
    assert owner("trafficmas/agents/intersection.py") == "part2"
    assert owner("trafficmas/agents/vehicle.py") == "part3"
    assert owner("trafficmas/contracts.py") == "shared"


def test_who_may_edit_what():
    assert editable_by("part1") == {"part1"}
    assert editable_by("part2") == {"part2", "part3", "shared"}   # maintainer, helps with part 3
    assert editable_by("part3") == {"part3"}
    assert editable_by("part4") == {"part4"}

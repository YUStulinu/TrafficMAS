"""Signal controllers and the registry used by scenarios and experiments."""
from __future__ import annotations

from trafficmas.control.base import BaseController
from trafficmas.control.classic import ActuatedController, FixedTimeController, MaxPressureController
from trafficmas.control.negotiation import NegotiationController

CONTROLLERS = {
    "fixed": (FixedTimeController, {}),
    "actuated": (ActuatedController, {}),
    "max_pressure": (MaxPressureController, {}),
    "negotiation": (NegotiationController, {}),
    "negotiation_coord": (NegotiationController, {"coordination": True}),
}


def make_controller(name: str, params: dict | None = None) -> BaseController:
    cls, defaults = CONTROLLERS[name]
    return cls(**{**defaults, **(params or {})})


def uses_coordination(name: str, params: dict | None = None) -> bool:
    return bool({**CONTROLLERS[name][1], **(params or {})}.get("coordination", False))


__all__ = ["CONTROLLERS", "BaseController", "make_controller", "uses_coordination"]

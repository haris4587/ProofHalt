# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

"""ProofHalt Studionet demo target.

This contract is deliberately non-financial. It provides an observable,
transaction-backed incident and one-way remediation state for ProofHalt's public
Studionet demonstration without accepting assets or pretending that Studio can
execute the EVM Guardian bridge.
"""

from genlayer import *
import typing


class ProofHaltStudionetTarget(gl.Contract):
    owner: Address
    vulnerable: bool
    incident_active: bool
    simulated_loss_events: u32
    patched_at_event: u32

    def __init__(self):
        self.owner = gl.message.sender_address
        self.vulnerable = True
        self.incident_active = False
        self.simulated_loss_events = u32(0)
        self.patched_at_event = u32(0)

    @gl.public.write
    def simulate_unauthorized_withdrawal(self) -> None:
        if not self.vulnerable:
            raise gl.vm.UserError("DEMO_VULNERABILITY_PATCHED")
        self.simulated_loss_events = u32(int(self.simulated_loss_events) + 1)
        self.incident_active = True

    @gl.public.write
    def apply_one_way_patch(self) -> None:
        if gl.message.sender_address != self.owner:
            raise gl.vm.UserError("DEMO_OWNER_ONLY")
        if not self.vulnerable:
            return
        self.vulnerable = False
        self.incident_active = False
        self.patched_at_event = self.simulated_loss_events

    @gl.public.view
    def get_security_state(self) -> dict[str, typing.Any]:
        return {
            "demo_only": True,
            "accepts_assets": False,
            "owner": self.owner.as_hex,
            "vulnerable": self.vulnerable,
            "incident_active": self.incident_active,
            "simulated_loss_events": int(self.simulated_loss_events),
            "patched_at_event": int(self.patched_at_event),
        }

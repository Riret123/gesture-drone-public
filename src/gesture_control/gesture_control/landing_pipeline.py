"""Offline fail-closed composition of observation checks and landing proposal.

This module has no transport. Camera-axis proposals are NOT MAVROS setpoints.
"""
from dataclasses import dataclass
from .landing import LandingController, LandingCommand
from .landing_candidates import CandidateGate, CandidateFrame
from .landing_motion import MotionGate


@dataclass(frozen=True)
class PipelineResult:
    observation_reason: str
    motion_reason: str | None
    proposal: LandingCommand


class OfflineLandingPipeline:
    """Acquire in search; any later rejected observation leads to terminal abort.

    No automatic reset/reacquisition, no inferred contact and no flight authority.
    Existing LandingController's offline thresholds are preserved unchanged.
    """
    def __init__(self, candidates: CandidateGate, motion: MotionGate):
        if not isinstance(candidates, CandidateGate) or not isinstance(motion, MotionGate):
            raise ValueError('configured offline candidate and motion gates required')
        self.candidates = candidates
        self.motion = motion
        self.controller = LandingController()

    def update(self, frame: CandidateFrame | None, now_s: float,
               contact: bool = False, abort: bool = False) -> PipelineResult:
        if self.controller.state in ('abort', 'touchdown'):
            return PipelineResult('terminal_latched', None,
                                  self.controller.update(None))
        observation = self.candidates.evaluate(frame, now_s)
        if not observation.accepted:
            proposal = self.controller.update(None, contact, abort)
            return PipelineResult(observation.reason, None, proposal)
        movement = self.motion.evaluate(observation.position_m, frame.captured_s)
        proposal = self.controller.update(observation.position_m if movement.accepted else None,
                                          contact, abort)
        return PipelineResult(observation.reason, movement.reason, proposal)

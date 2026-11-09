"""Bind local monotonic evidence to one explicitly configured session."""
from dataclasses import dataclass
from .sensor_evidence import EvidenceRecord, EvidenceReport, review_evidence
from .validation import finite


@dataclass(frozen=True)
class SessionEvidence:
    session_id: str
    record: EvidenceRecord


class EvidenceSession:
    def __init__(self, session_id: str, requirements):
        if type(session_id) is not str or not session_id or session_id.strip() != session_id:
            raise ValueError('exact nonempty evidence session required')
        # Validate policy now, without storing a mutable caller-owned list.
        review_evidence(requirements, [], 0.)
        self.session_id = session_id
        self.requirements = tuple(requirements)
        self._last_now_s = None

    def review(self, envelopes, now_s: float) -> EvidenceReport:
        if not finite(now_s) or now_s < 0:
            raise ValueError('nonnegative finite session clock required')
        if self._last_now_s is not None and now_s < self._last_now_s:
            return EvidenceReport('INCOMPLETE', (('<session>', 'clock_reversed'),))
        self._last_now_s = now_s
        if not isinstance(envelopes, (tuple, list)):
            raise ValueError('explicit session evidence list required')
        findings, records = [], []
        for envelope in envelopes:
            if not isinstance(envelope, SessionEvidence):
                findings.append(('<session>', 'invalid_envelope'))
                continue
            if type(envelope.session_id) is not str or envelope.session_id != self.session_id:
                findings.append(('<session>', 'wrong_session'))
                continue
            records.append(envelope.record)
        result = review_evidence(self.requirements, records, now_s)
        return EvidenceReport('INCOMPLETE' if findings else result.status,
                              tuple(findings) + result.findings)

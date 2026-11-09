"""Offline evidence completeness/freshness, never flight authorization."""
from dataclasses import dataclass
from .validation import finite


ORIGINS = frozenset({'human_attestation', 'measurement', 'simulation', 'source_review'})


def _identity(value):
    return type(value) is str and bool(value) and value.strip() == value


@dataclass(frozen=True)
class EvidenceRequirement:
    key: str
    scope: str
    revision: str
    max_age_s: float
    allowed_origins: tuple

    def __post_init__(self):
        if not all(_identity(v) for v in (self.key, self.scope, self.revision)):
            raise ValueError('exact requirement identity required')
        if not finite(self.max_age_s) or self.max_age_s <= 0:
            raise ValueError('positive finite evidence age limit required')
        if (type(self.allowed_origins) is not tuple or not self.allowed_origins
                or any(type(v) is not str or v not in ORIGINS for v in self.allowed_origins)
                or len(set(self.allowed_origins)) != len(self.allowed_origins)):
            raise ValueError('explicit distinct recognized origins required')


@dataclass(frozen=True)
class EvidenceRecord:
    key: str
    scope: str
    revision: str
    origin: str
    observed_s: float
    reference: str
    passed: bool


@dataclass(frozen=True)
class EvidenceReport:
    status: str
    findings: tuple


def review_evidence(requirements, records, now_s: float) -> EvidenceReport:
    """Check supplied metadata against explicit requirements.

    reference is an opaque local audit identifier, not a URL to fetch or a command.
    Completeness does not authenticate records or verify the referenced evidence.
    Extra evidence keys reject so an operator cannot accidentally review the wrong
    configuration. Empty requirements reject rather than pass vacuously.
    """
    if not finite(now_s) or now_s < 0:
        raise ValueError('nonnegative local monotonic time required')
    if (not isinstance(requirements, (tuple, list)) or not requirements
            or any(not isinstance(r, EvidenceRequirement) for r in requirements)):
        raise ValueError('nonempty validated requirements required')
    if not isinstance(records, (tuple, list)):
        raise ValueError('explicit record list required')
    keys = [r.key for r in requirements]
    if len(set(keys)) != len(keys):
        raise ValueError('duplicate requirement keys')
    findings = []
    by_key = {}
    for record in records:
        if not isinstance(record, EvidenceRecord):
            findings.append(('<record>', 'invalid_record'))
            continue
        if not _identity(record.key):
            findings.append(('<record>', 'invalid_key'))
            continue
        if record.key in by_key:
            findings.append((record.key, 'duplicate_record'))
            continue
        by_key[record.key] = record
        if record.key not in keys:
            findings.append((record.key, 'unexpected_record'))
    for requirement in requirements:
        key = requirement.key
        record = by_key.get(key)
        if record is None:
            findings.append((key, 'missing'))
            continue
        if record.scope != requirement.scope or type(record.scope) is not str:
            findings.append((key, 'wrong_scope'))
        if record.revision != requirement.revision or type(record.revision) is not str:
            findings.append((key, 'wrong_revision'))
        if type(record.origin) is not str or record.origin not in requirement.allowed_origins:
            findings.append((key, 'unaccepted_origin'))
        if not finite(record.observed_s) or record.observed_s < 0 or record.observed_s > now_s:
            findings.append((key, 'invalid_time'))
        elif now_s - record.observed_s > requirement.max_age_s:
            findings.append((key, 'expired'))
        if not _identity(record.reference):
            findings.append((key, 'missing_reference'))
        if type(record.passed) is not bool:
            findings.append((key, 'invalid_result'))
        elif not record.passed:
            findings.append((key, 'failed'))
    return EvidenceReport('INCOMPLETE' if findings else 'METADATA_COMPLETE', tuple(findings))

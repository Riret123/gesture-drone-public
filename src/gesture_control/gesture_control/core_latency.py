"""Bounded timing statistics. Measurements do not authorize or modify commands."""
from collections import deque
import math
import threading
from .validation import finite


class LatencyLedger:
    def __init__(self, max_samples=1000, budget_ms=100.):
        if type(max_samples) is not int or not 1 <= max_samples <= 100000:
            raise ValueError('max_samples must be an integer in 1..100000')
        if not finite(budget_ms) or budget_ms <= 0:
            raise ValueError('budget_ms must be finite and positive')
        self._samples = deque(maxlen=max_samples)
        self.budget_ms = budget_ms
        self._total = self._over = 0
        self._lock = threading.Lock()

    def record(self, capture, inference_start, inference_end, dispatch):
        times = (capture, inference_start, inference_end, dispatch)
        if (not all(finite(t) and t >= 0 for t in times)
                or any(b < a for a, b in zip(times, times[1:]))):
            return False
        stages = tuple((b-a)*1000 for a, b in zip(times, times[1:]))
        total = (dispatch-capture)*1000
        if not all(math.isfinite(v) for v in (*stages, total)):
            return False
        with self._lock:
            self._samples.append((*stages, total))
            self._total += 1
            self._over += total > self.budget_ms
        return True

    def summary(self):
        with self._lock:
            samples = tuple(self._samples)
            result = {'samples_retained': len(samples), 'samples_total': self._total,
                      'over_budget_total': self._over, 'budget_ms': self.budget_ms}
        names = ('capture_to_inference_ms', 'inference_ms', 'dispatch_ms', 'total_ms')
        for index, name in enumerate(names):
            values = sorted(sample[index] for sample in samples)
            result[name] = (None if not values else {
                'p50': values[math.ceil(.5*len(values))-1],
                'p95': values[math.ceil(.95*len(values))-1], 'max': values[-1]})
        return result

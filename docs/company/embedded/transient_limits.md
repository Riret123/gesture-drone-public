# R02 E03 - limitations of scalar peak budgeting
Peak amperes alone cannot select a regulator or fuse. Duration, repetition rate, startup profile, source impedance, capacitor ESR, cable inductance, driver regeneration and protection trip curves matter. A source may tolerate one short peak but overheat under repeated pulses.

Current budget sums peaks conservatively but has no time waveform, thermal model, voltage droop or regeneration model. Its WITHIN_ARITHMETIC_LIMITS result cannot close those hazards. Before selecting hardware, obtain peak duration and startup traces under the actual load and compare manufacturer operating envelopes with margin.

No powered testing is authorized by this document. R03 can add offline waveform arithmetic with explicit sampling assumptions; real measurement remains external evidence.

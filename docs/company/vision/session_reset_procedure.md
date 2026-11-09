# R02 V02 - capture session reset procedure
Stop the offline consumer; record why the source restarted; identify the new capture session from trusted local configuration; construct a new gate; retain the old rejection log separately. Never accept an arbitrary incoming session as a reset request.

Do not infer a reset from sequence zero, camera reconnect, clock reversal or a stale sample. Those conditions reject until the experiment owner explicitly reinitializes. A genuine camera reboot can reset sequence/time, so automatically preserving a running controller across it is unsafe without a separately reviewed reacquisition state.

The gate does not persist across process restarts; restart replay protection remains a system-level open item. No random session generation or cryptographic identity is provided.

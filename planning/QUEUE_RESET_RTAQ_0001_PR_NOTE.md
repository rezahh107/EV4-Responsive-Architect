# Queue Reset PR Note

This PR resets the active queue after the responsive-tree architecture refactor.

The legacy RQ lineage remains historical. The active queue now uses RTAQ task identifiers.

This PR does not create submitted evidence, modify Issue #8, run a pilot, or upgrade readiness claims.

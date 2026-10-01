# Windows M1 attempt A: retained infrastructure stop

Execution source: 519c3a8. Runner status STOPPED, reason
backend_port_state_unknown, at the pre-start gate for B2_F00.
Elapsed 5.059760799980722 seconds; recorded operations 0; product calls,
proxy POSTs and upstream attempts all 0. No backend start occurred.
Private report retains 40,488,466 bytes including prelaunch source snapshots.

A separate native socket probe with a five-second timeout returned Windows
10061 (connection refused) after 2.0314095000503585 seconds. The runner's
one-second probe expired too early. Revision increases that probe to five
seconds; existing listeners and remaining unknown states still stop.
The stopped capture is preserved and excluded from completed operation counts.
A new directory is required for the corrected M1 attempt. The existing
reservation ends at 2026-10-01T08:45:00Z and is not extended.

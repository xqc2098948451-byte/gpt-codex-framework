# GitHub Repository Binding

This management project is bound to the stable GitHub repository ID in
`CONTROL.github.repository_id`. Full name and default branch are durable
metadata; the local remote name is runtime-only. Reject foreign or ambiguous
repositories before state or Git mutation. Never force-push or rewrite history.

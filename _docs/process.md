- Tasks are Github issues
- Commit Regularly
- Every issue carries `mvp` or `post-mvp` - `post-mvp` means it waits until after the MVP ships. A follow-up issue filed while grooming (an out-of-scope item split out of the task being groomed) is `post-mvp` by default, unless it's clearly still needed for the MVP to work.

Roles

- PM - grooms a task before anyone implements it, follow _docs/team/pm.md_
- Software Engineer - implements one groomed task at a time, follow _docs/team/software-engineer.md_
- qa-engineer - tests the work of a Software Engineer, follow _docs/team/qa-engineer.md_

Orchestrator

The main session is the orchestrator. It launches the PM, the engineer
and QA as subagents. It does not groom, implement or test itself.

Lifecycle

1. Pick the next open issue from the backlog
2. PM grooms it
3. Engineer implements it
4. QA verifies it
5. On FAIL, back to step 3 with the QA comment as input
6. On PASS, commit and close the issue
7. Repeat until the backlog is empty

Rules

- One issue at a time
- Do not skip step 2, even when the task looks obvious
- The engineer does not close the issue, QA does not fix the code
- Do not commit until the tests pass
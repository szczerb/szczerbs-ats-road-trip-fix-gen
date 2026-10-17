# Incident Template

Use one folder per incident with this minimum structure:

- `README.md`
- `PROBLEM_STATEMENT.md`
- `DEBUGGING_PLAN.md`
- `STEP_BY_STEP.md`
- `RESULTS.md`

Link the incident from its active task. Record the date, exact ATS/DLC/mod versions and load order, expected and actual behavior, reproduction steps, and evidence labels. Separate static-file observations from in-game results; use a disposable or copied profile for game experiments. Record unavailable evidence and failed hypotheses as well as successful checks.

Keep large logs and game/mod assets under ignored `local_outputs/` locations; put small authored summaries and reproducible collection instructions here. Planned feature research without a reproduced failure stays in its task.

Optional additions:

- `LOGGING_SETUP.md`
- `deep-dive/`

# Git identity and maintaining a first public repository

Reviewed 2026-10-18. This records the user's deliberate identity choice and general public-repository practice; no account, Git configuration, commit metadata or history was changed.

## Correction to the earlier privacy finding

**Documented — user clarification:** `szczerb (legacy placeholder email)` is an intentional pseudonym and placeholder address, used consistently on this machine. **Observed locally:** all 33 commits reachable at baseline `d2e7d9c` use this same author/committer identity. The earlier review incorrectly treated a non-`noreply` email as evidence of a private mailbox. That inference is withdrawn. There is no reason to rewrite this history to remove that placeholder.

**Documented:** `.invalid` is reserved for deliberately invalid domain names in [RFC 2606, section 2](https://www.rfc-editor.org/rfc/rfc2606.html#section-2). The separate presence of local account names in documentation paths remains a disclosure/readability choice; it does not turn the commit address into personal contact information.

## Public identity options

| Choice | Practical result |
| --- | --- |
| Alias plus intentional placeholder, as here | Commits remain normal Git commits and can be published. The address is not a usable contact channel; GitHub profile attribution should not be assumed. |
| Alias plus account-specific GitHub `noreply` address | Keeps a private mailbox out of commit headers while supporting GitHub attribution. Copy the exact address shown in account settings. |
| Public professional name/address | Can connect professional identity and contact details to the work; it is an optional disclosure, not a requirement for this repository. |

**Documented:** the [Git author name](https://docs.github.com/en/get-started/git-basics/setting-your-username-in-git) is distinct from a GitHub login, and GitHub explicitly permits arbitrary name text for privacy. Git uses these author fields as metadata; they are not proof of account authentication or a verified legal identity.

GitHub [uses the configured commit email for attribution](https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address). Its [contribution troubleshooting guide](https://docs.github.com/en/account-and-profile/how-tos/contribution-settings/troubleshooting-missing-contributions) describes account-linked or provided `noreply` addresses and generic-address limitations. Publishing a repository and having every historical commit linked to an account are separate concerns. Missing profile attribution is not a license violation. Keep the present configuration until the user chooses otherwise.

For future multi-identity use, repository-local settings can separate personal and employer identities; changing settings affects future commits. It does not sanitize earlier commits. A [`.mailmap`](https://git-scm.com/docs/gitmailmap) can normalize displayed identities in supporting Git views; it does not erase original objects or their metadata. No identity rewrite is recommended for this intentional placeholder.

## A proportionate first public release

**Project recommendation:** keep the maintainership setup small. A useful README explains the problem, supported versions, reproducible commands, excluded/provided inputs and known limits. Add the chosen license and third-party notices, provide a normal test command, and identify how to report reproducible bugs. Our generator should document where users obtain their own game/mod inputs and what data the generated output contains.

State maintenance expectations honestly: a hobby utility can have best-effort support and a narrow compatibility scope. Publishing under an open license does not promise feature development or acceptance of every pull request. License warranties/disclaimers and any actual support contract are distinct; [the maintainer license guide](MAINTAINER_LICENSE_CHOICES.md) explains the legal distinctions and contribution options.

Issue/PR templates, CI, contribution rules and a code of conduct can be added when useful. No contributor agreement, governance structure, paid support promise, public contact mailbox, signed-commit policy or release automation is imposed by this advice. Before accepting external code, state the inbound contribution terms so future licensing choices remain understandable.

See [the content/history review](PUBLIC_REPOSITORY_REVIEW.md), [deeper map audit](DEEP_MAP_PARSER_PROVENANCE_REVIEW.md), [helper audit](DEEP_HELPER_PROVENANCE_REVIEW.md) and [license choices](MAINTAINER_LICENSE_CHOICES.md). These notes do not themselves publish the repository or select its license.

## Local paths in the publication review

**Observed locally — 2026-10-18, baseline `da76a0f`:** root verified a delegated GPT-6 Luna/medium read-only review using a prefix-pattern scan of tracked text. The checked prefixes represent the concrete Linux project home, Windows/WSL account home and generic game-cache path already recorded in the repository. There are **22 prefix matches on 19 lines in 15 files**: 16 artifact links on 13 lines, four screenshot-location lines, one Windows cache-length test fixture and one generic game-cache line. This is a bounded path inventory, not an exhaustive personal-data scan. Machine-readable evidence remains ignored under `local_outputs/work/2026-10-18_19-56-58/local-path-review.json`. New explanatory documentation is outside those baseline counts.

| Location | What is recorded | Publication implication |
| --- | --- | --- |
| [Current map handoff](MOD_METADATA_MAP_NAMES_1_61_R8_R3.md) and older reports | Absolute Linux links to ignored output archives and research reports, including the local account and repository folder | Readers can see those names. The links fail on another machine and do not supply the linked files. |
| [Gameplay evidence](VALIDATION_RESULTS.md) and screenshot inspection notes | Windows/WSL account paths to Pictures or the game's screenshot folder | Reveals the local account name and folder layout; it does not upload the screenshot. |
| `tests/test_bulk_run.py`, baseline line 260 | A synthetic Windows game-home string used to reproduce an observed icon-cache path-length budget | This test does not read that home directory. Its length matters to the regression case; a neutral replacement should preserve the intended length/budget. |
| [Icon-cache incident](../incidents/INC-0001-connector-icon-cache/PROBLEM_STATEMENT.md) | A generic virtual game-cache path with a placeholder image hash | Reproducible failure context, not a concrete user's home directory. |

**Observed locally:** the delegate's `src/`, `tests/` and example scan, reviewed by root, found no runtime default hardcoding these user-specific paths. The concrete user-home path in code is the synthetic test fixture. The generator consumes supplied paths; this finding does not promise portability of every tool or command on every operating system.

**Project recommendation:** before a public release, replace machine-specific documentation links with repository-relative artifact identifiers or plain filenames and explicitly state that local artifacts are excluded. Merely converting to a relative link will not make an ignored file available to a public clone. Describe screenshot folders with environment placeholders, and optionally neutralize the test fixture while retaining its length-based purpose. This improves readability and avoids unnecessary disclosure; the observed paths alone are not passwords or access credentials.

No paths or history are sanitized by this explanation. Removing a path from the current checkout would leave it in earlier commits if the full history were published. History rewriting or publishing a fresh export would be separate, explicitly chosen work. `.gitignore` excludes artifact contents; it does not hide path strings written inside tracked documentation.

**Subsequent license decision:** [AGPL-3.0-only](../../LICENSING.md) is now applied under [ADR-0016](../architecture/decisions/ADR-0016-license-project-under-agpl-v3.md); local-path disclosure and identity configuration remain separate decisions.

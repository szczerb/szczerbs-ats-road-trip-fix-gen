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

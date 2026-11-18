# Security

Please report security problems **privately** — open a GitHub security advisory
("Report a vulnerability" on the repository's *Security* tab) instead of a public issue.
Include what you found, how to reproduce it and what an attacker could do with it.

What Ura protects and how is described in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#security-model).

Operators:
- Compare the server fingerprint when registering a hub, and the safety code with each partner.
- Keep the hub website on your local network.
- Back up `identity.key` (hub) and `tls.key` (server) privately; never publish them.

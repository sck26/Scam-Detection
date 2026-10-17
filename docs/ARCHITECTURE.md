# Planned system architecture

ScamGuard is iOS-first and tactic-based. The product should identify observable
manipulation—urgency, impersonation, credential requests, unusual payment,
secrecy, and related tactics—rather than memorize a list of scam types. Scam
categories remain reporting dimensions, not detector logic.

## Client and extensions

The iOS app owns consent, settings, explanations, scan history, and the optional
close circle. A compact on-device model provides the fastest, most private first
pass and keeps basic protection available offline. It produces a calibrated
score, Safe/Suspicious/Dangerous level, and tactic evidence. The app should show
why a message was flagged and give the user a safe next action without claiming
certainty.

Platform extensions are deliberately narrow: an IdentityLookup Message Filter
extension for unknown-sender SMS/MMS, the approved caller-identification
extension, an optional Network Extension where entitlements and product scope
justify DNS/content filtering, and a Safari web extension for user-authorized
page/link checks. Each extension obeys its platform sandbox and sends only the
minimum permitted data. Email connectors are explicit opt-in integrations;
credentials remain server-side and use narrow OAuth scopes.

## Backend path

The future backend exposes a versioned, stateless API behind authenticated rate
limits. A request is normalized and checked against a cache before expensive
analysis. Cache misses enqueue work; independently scalable workers call URL
reputation, rules, classical models, and language-model services. Workers combine
signals into a calibrated result with tactic evidence and provenance. Postgres
stores accounts, consent, connector metadata, close-circle relationships,
notification state, model/policy versions, and auditable decisions. A separate
cache holds bounded-lifetime analysis results and rate-limit state.

The synchronous path returns an existing result or a bounded quick analysis.
Longer work completes asynchronously through the queue and can update the app by
APNs. Close-circle alerts require explicit consent, relationship verification,
severity policy, deduplication, quiet-hours handling, and revocation. Notification
payloads contain minimal sensitive detail; authorized clients fetch the full
explanation after authentication.

## Analyze once, reuse safely

Identical scams should be analyzed once. The cache key is a privacy-preserving
digest of a carefully normalized artifact plus detector version, policy version,
channel, locale, and any other input that can change the answer. Results have
source-aware expiration and can be invalidated when feeds, models, or policy
change. Raw user content is not used as a global cache key, logged, or retained
by default. Highly personal text may be restricted to an account-scoped cache or
on-device analysis so cross-user reuse cannot leak private content.

## Operational boundaries

Services are horizontally scalable and idempotent: the API is stateless, queue
messages carry stable job IDs, and workers tolerate retries. External providers
sit behind adapters with timeouts, circuit breakers, quotas, and recorded terms
of use. Encryption in transit/at rest, least privilege, regional retention,
deletion workflows, audit logs, model/version observability, and incident
response are system requirements—not later polish.

Every detector release is evaluated against the committed hand-labeled set and
public-data baselines. Promotion gates emphasize false-positive rate alongside
precision and recall, with per-channel, per-category, and tactic metrics. Phase 0
implements none of these production services; it defines the taxonomy, data
contracts, test set, and evaluation harness they must satisfy.


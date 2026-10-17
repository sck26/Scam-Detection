# Accounts and entitlements checklist

Start these items during Phase 0. Approval, organization verification, endpoint
validation, and App Review can take longer than implementation. Record owners,
renewal dates, and status in the team's private operations system—not in Git.

## Apple Developer Program

- [ ] Choose the legal entity that will publish the app and confirm its legal
  name, address, D-U-N-S details (for an organization), authority to agree to
  contracts, and a monitored organization-domain email address.
- [ ] Enroll in the [Apple Developer Program](https://developer.apple.com/programs/enroll/).
- [ ] Invite at least two trusted administrators; require strong account
  security and avoid a single-person recovery path.
- [ ] Accept current agreements and complete App Store Connect tax and banking
  setup when distribution is approaching.
- [ ] Reserve final bundle identifiers for the containing app and each extension.
  Do not use `scamguard` as a production reverse-DNS prefix until ownership and
  naming are approved.
- [ ] Create separate development and production APNs keys, with documented
  rotation and revocation owners.

## Apple capabilities and extension work

Confirm every capability in Certificates, Identifiers & Profiles and in a small
proof-of-entitlement Xcode project before scheduling the feature. Apple can
change availability by platform, distribution method, region, and account.

### Message Filter extension (unknown-sender SMS/MMS)

- [ ] Add an IdentityLookup Message Filter app-extension target and test the
  user enablement flow on a physical device.
- [ ] Design within Apple's boundary: the extension receives SMS/MMS from
  unknown senders only—not iMessage and not senders in Contacts.
- [ ] Plan an on-device first decision. The extension cannot access the network
  directly; when permitted, the system performs one deferral to the associated
  HTTPS service named by `ILMessageFilterExtensionNetworkURL`.
- [ ] Configure and validate the associated domain/service before App Review.
- [ ] Re-check the current [SMS/MMS filtering documentation](https://developer.apple.com/documentation/identitylookup/sms-and-mms-message-filtering)
  when implementation starts.

### Caller identification and blocking

- [ ] Prototype the appropriate IdentityLookup/CallKit extension for the
  supported OS versions; document whether the product uses an on-device Call
  Directory database, Live Caller ID Lookup, or both.
- [ ] For Live Caller ID Lookup, submit Apple's request early. It uses Apple
  relay servers and requires Apple to validate the service endpoints.
- [ ] Budget time for server protocol implementation, endpoint validation,
  privacy review, device testing, and App Review.
- [ ] Track Apple's current [Live Caller ID Lookup requirements](https://developer.apple.com/documentation/identitylookup/getting-up-to-date-calling-and-blocking-information-for-your-app).

### Network Extension for DNS/content filtering

- [ ] Decide whether the actual need is `dns-proxy`, `content-filter-provider`,
  or neither; do not request packet-tunnel access as a shortcut.
- [ ] Confirm the required Network Extension values are available for the
  intended platform and distribution profile, then enable the capability in
  Xcode and the App ID.
- [ ] If the account or distribution route requires managed-capability approval,
  submit the request with the narrow use case, data-flow diagram, privacy
  explanation, and test instructions. Even when self-service provisioning is
  available, expect close App Review scrutiny and allow lead time.
- [ ] Validate OS and device limitations before promising whole-device coverage.
- [ ] Use Apple's current [Network Extensions entitlement reference](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.networking.networkextension).

### Safari web extension

- [ ] Add the Safari Web Extension target only after URL-scanning behavior and
  minimum site permissions are defined.
- [ ] Request the smallest website access scope and provide a clear user control
  for enabling/disabling analysis.
- [ ] Plan App Store distribution and extension-specific review materials;
  Apple reviews extensions and their updates.
- [ ] Start from Apple's [Safari extensions guidance](https://developer.apple.com/safari/extensions/).

### Push notifications

- [ ] Enable Push Notifications for the App ID and add the Xcode capability.
- [ ] Create an APNs signing key in the team account; store the `.p8` file once
  in the secret manager because it cannot be downloaded again.
- [ ] Keep development and production topics/environments explicit and test
  token rotation, invalid-token cleanup, consent, quiet hours, and close-circle
  revocation.
- [ ] Never put message contents or sensitive analysis detail in a lock-screen
  notification by default.

## Cloud provider: choose AWS or GCP

- [ ] Select one provider using a short decision record; Phase 0 provisions
  nothing.
- [ ] Create the organization/root account with hardware-backed MFA, protected
  recovery details, and no routine root-user access.
- [ ] Create separate development, staging, and production projects/accounts.
- [ ] Configure least-privilege SSO roles and an audited emergency-access path.
- [ ] Set budget and billing alerts at multiple thresholds before creating paid
  resources; route alerts to at least two humans.
- [ ] Enable audit logs, security contacts, and region/data-residency decisions.
- [ ] Create a managed secret store (AWS Secrets Manager/Parameter Store or GCP
  Secret Manager) and define rotation ownership.

## Third-party accounts

- [ ] **Anthropic:** create an organization/workspace and a development API key;
  set spend limits and log-retention/privacy settings appropriate for message
  analysis before sending any user data.
- [ ] **Google Safe Browsing:** create a dedicated cloud project, enable the
  selected API, restrict the key by API and workload, and review caching and
  display requirements for the chosen service tier.
- [ ] **Twilio:** verify the organization, enable MFA, create least-privilege
  subaccounts/API keys per environment, configure spend/fraud alerts, and plan
  phone-number/compliance registration only when the feature needs it.
- [ ] **PhishTank (optional):** register an application key and review current
  feed terms and rate limits. The key is optional in local data preparation.
- [ ] **Gmail OAuth:** create a Google Cloud OAuth app, scopes, consent screen,
  privacy-policy URLs, test users, and verification plan. Request only the
  narrowest scopes; restricted scopes can require verification/security review.
- [ ] **Microsoft OAuth:** create a Microsoft Entra app registration, redirect
  URIs, Graph permissions, publisher verification, consent plan, and separate
  credentials per environment.

## Secret locations

| Secret | Local development | CI | Runtime | Never store in |
|---|---|---|---|---|
| API keys and feed keys | Untracked `.env` or OS keychain | GitHub Actions environment/organization secrets | Cloud secret manager | Git, `.env.example`, logs |
| OAuth client secrets | Untracked secret file or OS keychain | Protected CI secret | Cloud secret manager | Mobile app bundle, Git |
| APNs `.p8` key | Restricted OS keychain/encrypted vault | Protected CI secret only if signing requires it | Cloud secret manager/HSM-backed store | Git, shared drive, app bundle |
| Database/cache credentials | Local untracked `.env` | Ephemeral CI service credentials | Workload identity or secret manager | Source, reports, analytics |
| Signing certificates/profiles | Xcode-managed account or encrypted signing vault | Protected signing store | Not on application servers | Git, general file shares |

`.env.example` contains names only. Production workloads should prefer short-lived
workload identity over long-lived keys. Define rotation, revocation, access
review, incident response, and offboarding before production credentials exist.


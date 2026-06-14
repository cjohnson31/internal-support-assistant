# Service Accounts

Service accounts are non-human identities used by applications to authenticate with internal APIs and infrastructure.

## Creating a Service Account

1. Go to **Atlas → Service Accounts → Create New**
2. Enter a descriptive name following the convention: `svc-<team>-<purpose>` (e.g., `svc-payments-db-reader`)
3. Select the namespace the account belongs to
4. Choose the required API scopes
5. Click **Create** — the credentials (client ID and secret) are shown once; copy them immediately

**Important:** Credentials are displayed only at creation time. If lost, you must rotate them.

## Rotating Credentials

If credentials are lost or compromised:

1. Go to **Atlas → Service Accounts → [account name] → Security**
2. Click **Rotate Credentials**
3. A new client secret is generated immediately; the old one remains valid for 24 hours (grace period)
4. Update your application config with the new secret
5. The old secret automatically expires after the 24-hour window

For emergency revocation (credential leak), click **Revoke Immediately** instead — this disables the old secret instantly with no grace period. Note that this may cause downtime for services using the old credentials.

## Service Account Limits

- Each namespace can have up to **25 service accounts**
- Each service account can hold up to **10 API scopes**
- Service accounts inactive for 90 days are flagged for review
- Accounts inactive for 180 days are automatically disabled

## Auditing

All service account actions (creation, rotation, scope changes) are logged in the **Audit Log** under Atlas → Compliance → Audit Log. Logs are retained for 1 year.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Unauthorized" errors | Check that the service account's scopes include the API you're calling |
| "Account disabled" | The account was inactive for 180+ days — re-enable it in the admin console or create a new one |
| "Rate limited" | Service accounts share the namespace rate limit (1000 req/min) — check other accounts in your namespace |
| Credentials not working after rotation | The old secret has a 24h grace period — make sure you're using the new one |

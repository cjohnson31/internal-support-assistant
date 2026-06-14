# Incident Response Runbook

## Severity Levels

| Level | Definition | Response Time | Example |
|-------|-----------|---------------|---------|
| **SEV-1** | Service fully down, customer-facing impact | 15 minutes | Payment processing is failing for all users |
| **SEV-2** | Service degraded, partial customer impact | 1 hour | Search results are slow but functional |
| **SEV-3** | Internal tooling broken, no customer impact | 4 hours | Staging deployments are failing |
| **SEV-4** | Minor issue, cosmetic or non-urgent | Next business day | Dashboard chart rendering incorrectly |

## Declaring an Incident

1. Go to **Atlas → Incidents → Declare Incident**
2. Select the severity level
3. Describe the impact in one sentence
4. Select the affected service(s) from the service catalog
5. Click **Declare** — this automatically:
   - Creates a dedicated Slack channel `#inc-<number>`
   - Pages the on-call engineer for the affected service
   - Starts the incident timer

## During an Incident

- **Incident Commander (IC)**: The on-call engineer for the primary affected service. Coordinates the response.
- **Communication Lead**: Posts status updates every 15 minutes (SEV-1) or 30 minutes (SEV-2) to #incidents
- All investigation and discussion happens in the dedicated `#inc-` channel

## Resolving an Incident

1. Confirm the issue is fixed and monitoring shows recovery
2. In Atlas, click **Resolve Incident**
3. Write a brief resolution summary

## Post-Incident Review (PIR)

- Required for all SEV-1 and SEV-2 incidents
- Must be completed within **5 business days** of resolution
- Template available at Atlas → Incidents → [incident] → Create PIR
- PIR should include: timeline, root cause, contributing factors, action items with owners and due dates
- PIRs are blameless — focus on systems and processes, not individuals

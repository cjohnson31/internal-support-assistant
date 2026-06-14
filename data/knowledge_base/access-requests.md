# Access Requests

Access requests are the formal process for gaining permissions to Atlas resources.

## When You Need an Access Request

You need an access request to:
- Change your Atlas role (e.g., Viewer → Developer)
- Access a namespace you're not a member of
- Gain production deployment permissions
- Access sensitive data scopes on a service account

You do NOT need an access request to:
- View public dashboards
- Create service accounts in your own namespace
- Deploy to dev or staging (if you already have Developer role)

## Submitting a Request

1. Go to **Atlas → Access Requests → New Request**
2. Select the resource type (role change, namespace access, scope grant)
3. Provide a business justification (required — requests without justification are auto-rejected)
4. Select the duration: **permanent** or **temporary** (1 day to 90 days)
5. Click **Submit**

Your request is routed to the appropriate approver:
- **Role changes**: Your direct manager
- **Namespace access**: The namespace owner
- **Sensitive scopes**: Security team + your manager (dual approval)

## Approval SLA

- Standard requests: **2 business days**
- Urgent requests (mark as urgent with justification): **4 hours**
- Requests not acted on within 5 business days are auto-escalated to the approver's manager

## Temporary Access

Temporary access automatically expires at the end of the granted period. You'll receive a reminder 3 days before expiration. To extend, submit a new access request referencing the original.

## Revoking Access

Managers can revoke access at any time from **Atlas → Team → [member] → Revoke Access**. Revocation takes effect immediately.

## Auditing

All access request decisions (approvals, rejections, revocations) are logged in the Audit Log and retained for 1 year.

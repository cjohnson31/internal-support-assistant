# Getting Started with Atlas

Atlas is the company's internal platform for managing service accounts, deployments, and infrastructure access requests.

## Accessing Atlas

1. Navigate to https://atlas.internal.company.com
2. Sign in with your corporate SSO credentials (same as email login)
3. First-time users are automatically provisioned with a **Viewer** role

If you cannot access Atlas, verify that your SSO account is active by checking with IT at #it-help on Slack.

## Roles and Permissions

Atlas has four roles, each inheriting the permissions of the one below it:

- **Viewer**: Read-only access to dashboards and service catalogs
- **Developer**: Can create and manage service accounts, deploy to staging
- **Team Lead**: Can approve access requests, deploy to production, manage team members
- **Admin**: Full platform access, can manage roles and global settings

Your role is assigned by your team lead. To request a role change, submit an Access Request (see Access Requests guide).

## Key Concepts

- **Service Account**: A non-human identity used by applications to authenticate with internal APIs
- **Deployment Pipeline**: A configured CI/CD flow that builds, tests, and deploys your service
- **Access Request**: A formal request to gain permissions for a resource, requiring manager approval
- **Namespace**: A logical grouping of services and resources owned by a team

# Deployments

Atlas manages deployment pipelines for all internal services.

## Deployment Environments

| Environment | Purpose | Who Can Deploy |
|-------------|---------|----------------|
| **dev** | Local integration testing | Any Developer |
| **staging** | Pre-production validation | Any Developer |
| **production** | Live traffic | Team Lead or above |

## Creating a Deployment Pipeline

1. Go to **Atlas → Deployments → New Pipeline**
2. Connect your GitHub repository
3. Select the branch to track (default: `main`)
4. Configure build steps (Atlas auto-detects Dockerfile, package.json, or pyproject.toml)
5. Set the target environment
6. Click **Create Pipeline**

## Deploying

### Manual Deploy
1. Go to **Atlas → Deployments → [pipeline name]**
2. Select the commit or tag to deploy
3. Click **Deploy**
4. Monitor progress in the deployment log

### Auto-Deploy
Enable auto-deploy in pipeline settings to deploy automatically when the tracked branch receives a push. Auto-deploy is available for **dev** and **staging** only — production always requires manual approval.

## Rollbacks

To roll back a production deployment:

1. Go to **Atlas → Deployments → [pipeline name] → History**
2. Find the previous healthy deployment
3. Click **Rollback to This Version**
4. Confirm the rollback — this takes effect within 60 seconds

Rollbacks redeploy the previous container image; they do not revert database migrations. If a rollback is needed due to a bad migration, contact the Platform team in #platform-eng.

## Deployment Limits

- Maximum **3 concurrent deployments** per namespace
- Build timeout: **15 minutes** (configurable up to 30 minutes)
- Container image max size: **2 GB**
- Deployment history retained for **90 days**

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Build fails with "OOM" | Your build exceeds the 4 GB memory limit — optimize your build or request a larger builder in #platform-eng |
| Deploy stuck in "Pending" | You've hit the 3-concurrent-deployment limit — wait for an active deploy to finish or cancel one |
| "Permission denied" on production deploy | Only Team Lead or Admin roles can deploy to production — ask your team lead |
| Health check failing after deploy | Your service must respond 200 on `/healthz` within 30 seconds of starting — check your startup time |

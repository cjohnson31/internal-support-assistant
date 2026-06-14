# VPN and Network Access

## VPN Setup

All Atlas resources are accessible only from the corporate network or via VPN.

### Installing the VPN Client

1. Download **GlobalConnect VPN** from the internal software portal at https://software.internal.company.com
2. Install and open the client
3. Server address: `vpn.company.com`
4. Authenticate with your SSO credentials + MFA

### VPN Profiles

| Profile | Use Case |
|---------|----------|
| **General** | Email, Slack, internal wikis |
| **Engineering** | Atlas, GitHub Enterprise, CI/CD systems, internal APIs |
| **Full Tunnel** | Routes all traffic through corporate network — use only when required by compliance |

Select the **Engineering** profile to access Atlas and related infrastructure.

## Network Troubleshooting

| Problem | Solution |
|---------|----------|
| VPN connects but Atlas won't load | Make sure you're on the **Engineering** profile, not General |
| "Certificate error" on VPN connect | Your VPN client needs updating — download the latest from the software portal |
| Frequent VPN disconnections | Check your internet connection; if stable, try switching VPN servers (Settings → Server List) |
| Can't reach internal APIs from local dev | Ensure VPN is connected with Engineering profile and your `/etc/hosts` isn't overriding internal DNS |

## Office Network

When on the office Wi-Fi (`CorpSecure`), VPN is not required for most resources. However, production environment access always requires VPN regardless of network.

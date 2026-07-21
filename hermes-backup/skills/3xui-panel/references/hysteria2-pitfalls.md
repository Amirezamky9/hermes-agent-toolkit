# Hysteria2 on 3x-ui — Debugging Notes (July 2026)

## Error Sequence During Creation

### Attempt 1: No streamSettings
```
infra/conf: Config: unknown transport protocol:
```
Xray needs to know the transport protocol. For Hysteria2, it must be UDP.

### Attempt 2: streamSettings with network: "udp" only (no version)
```
infra/conf: failed to build inbound handler for protocol hysteria > infra/conf: version != 2
```
The `version` field is mandatory in settings. Without it, Xray cannot determine the Hysteria protocol version.

### Attempt 3: version: 2 in settings, no streamSettings
```
proxy/hysteria: not hysteria transport
```
Even with version: 2, Xray still needs `streamSettings.network: "udp"` to confirm the transport.

### Attempt 4: version: 2 + streamSettings.network: "udp" ✅
Xray starts successfully. Both fields are required.

## Root Cause
The Xray Hysteria inbound handler requires:
1. `settings.version = 2` — to select the Hysteria2 protocol handler
2. `streamSettings.network = "udp"` — to configure the UDP transport layer

These are independent checks. Removing either one produces a different error message, making debugging confusing.

## Share Link Format
```
hy2://AUTH_PASSWORD@HOST:PORT?insecure=1&type=udp#REMARK
```
- `insecure=1` required when not using TLS
- `type=udp` specifies the transport

## Client Attachment
After creating the Hysteria2 inbound, clients must be explicitly attached:
```bash
POST /clients/{email}/attach
Body: {"inboundIds": [INBOUND_ID]}
```
The client is NOT automatically added to the new inbound.

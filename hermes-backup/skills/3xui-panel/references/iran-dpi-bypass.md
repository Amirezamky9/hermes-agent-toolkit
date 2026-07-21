# Iran DPI Bypass — Protocol Research (July 2026)

Sources: XTLS/Xray-core discussions, NexTunnel benchmarks (May 2026), ProxyPoland guide, DeepWiki Xray-examples.

## Benchmark Data (Helsinki server, May 2026)

| Protocol | Iran Mobile (Irancell 4G, ~5% loss) | Clean Network | DPI Resistance | Connection Success Rate |
|---|---|---|---|---|
| VLESS + Reality + XTLS-Vision | 43 Mbps | 94 Mbps | Highest | 99.1% |
| Hysteria2 (QUIC + Salamander) | 61 Mbps | 97 Mbps | High | 97.3% |
| Trojan (TLS) | 11 Mbps | 96 Mbps | Medium | 12.4% |
| VMess + WS + TLS | varies | varies | Low-Medium | varies |

Server-side CPU per 100 Mbps: Reality 4.2% / Hysteria2 6.8% / Trojan 1.9%

## How Reality Defeats DPI

1. **TLS 1.3 handshake impersonation** — ClientHello is byte-for-byte identical to Chrome 124+ visiting the dest site (JA3 fingerprint, ALPN, cipher suites, elliptic curves)
2. **XTLS-Vision padding** — TLS record sizes match statistical distribution of real browser traffic, defeating record-length analysis
3. **x25519 authentication** — Only clients with matching public key + short_id can tunnel. Unauthenticated probes (including DPI) get the real cover site
4. **Splice on Linux** — Zero-copy data transfer when TLS 1.3 detected, eliminating core IO overhead

## How Hysteria2 Defeats DPI

- QUIC + Salamander XOR obfuscation makes UDP flows look like random noise
- Per-stream flow control avoids TCP head-of-line blocking → 30-60% higher throughput on lossy links
- Structurally immune to TCP-only DPI inspection paths

## How Trojan Fails in Iran

- SNI points to VPN server's own domain → visible to SNI allowlist DPI
- Average survival: 2-7 days before SNI is added to filtering rules
- Only suitable for permissive corporate networks, not censorship environments

## Iran GFW Detection Methods (2026)

1. **Traffic volume analysis** — Heavy traffic on a single Reality IP triggers detection (tested: >200 users → blocked within 2 hours)
2. **SNI denylists** — Trojan and CDN domains (*.cloudfront.net, *.cloudflare.com) actively filtered
3. **TCP fragmentation reassembly** — Iran's DPI can now reassemble classic fragment packets, making `fragment` alone insufficient
4. **UDP throttling** — Some ISPs (MCI, Irancell) throttle all UDP above a volume threshold, degrading Hysteria2

## Best Practices for Iran

- Max 5-7 users per Reality server
- Use `www.microsoft.com:443` as Reality dest (most reliable, not blocked)
- Port 443 mandatory for Reality
- `fp=chrome` fingerprint required
- `flow: xtls-rprx-vision` mandatory for Vision mode
- NTP sync within 30 seconds (clock drift breaks Reality)
- Fresh IPs work better than old ones
- Provide Reality + Hysteria2 + CDN WS as 3-tier fallback

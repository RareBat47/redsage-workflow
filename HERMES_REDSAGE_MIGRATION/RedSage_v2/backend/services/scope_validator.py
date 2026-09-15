"""Scope target validation and matching.

Whitelist/blacklist entries are plain strings supplied by the analyst when
configuring a project scope. Supported entry forms:

- Domain or hostname: ``api.example.com`` (covers only that exact host)
- Wildcard domain: ``*.example.com`` (covers the apex domain and every
  subdomain at any depth, following common bug-bounty program notation)
- IPv4/IPv6 address: ``192.168.1.1`` (covers only that address)
- CIDR network: ``10.0.0.0/8`` (covers any address inside the network)

Matching is case-insensitive and ignores surrounding whitespace and trailing
FQDN dots. Wildcards are only allowed as a single leading ``*.`` label, and a
wildcard entry is never itself a concrete target host.
"""

import ipaddress
import re

_DOMAIN_RE = re.compile(r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-_]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}$")
_EXTRA_VALID_TARGETS = {"localhost", "target.local", "juice-shop.local"}
WILDCARD_PREFIX = "*."


def _normalize(value: str) -> str:
    """Lowercase, trim whitespace, and drop trailing FQDN dots."""
    return value.strip().lower().rstrip(".")


def _is_valid_domain(value: str) -> bool:
    return bool(_DOMAIN_RE.match(value))


def _parse_ip(value: str):
    try:
        return ipaddress.ip_address(value)
    except ValueError:
        return None


def _parse_network(value: str):
    try:
        return ipaddress.ip_network(value, strict=False)
    except ValueError:
        return None


def is_valid_target(target: str) -> bool:
    """Return True when *target* is usable as a scope whitelist/blacklist entry."""
    target = target.strip()
    if not target:
        return False
    if target.startswith(WILDCARD_PREFIX):
        return _is_valid_domain(target[len(WILDCARD_PREFIX):])
    if _parse_network(target) is not None:
        return True
    return _is_valid_domain(target) or _normalize(target) in _EXTRA_VALID_TARGETS


def target_matches_scope_entry(target: str, entry: str) -> bool:
    """Return True when a concrete *target* host is covered by a scope *entry*.

    Rules:
    - Wildcard entry ``*.example.com`` covers the apex ``example.com`` and any
      subdomain (``api.example.com``, ``a.b.example.com``). Label boundaries
      are enforced, so ``evil-example.com`` and ``example.com.evil.com`` do
      NOT match.
    - A network entry (``10.0.0.0/8``; a bare IP is an implicit /32 or /128)
      covers target IP addresses inside the network.
    - Any other entry covers only the identical hostname or address.

    A wildcard-pattern target (``*.example.com``) is not a concrete host and
    never matches anything.
    """
    target_norm = _normalize(target)
    entry_norm = _normalize(entry)
    if not target_norm or not entry_norm or target_norm.startswith(WILDCARD_PREFIX):
        return False
    if entry_norm.startswith(WILDCARD_PREFIX):
        suffix = entry_norm[len(WILDCARD_PREFIX):]
        return target_norm == suffix or target_norm.endswith("." + suffix)
    network = _parse_network(entry_norm)
    if network is not None:
        address = _parse_ip(target_norm)
        return address is not None and address in network
    return target_norm == entry_norm


def is_target_whitelisted(target_host: str, in_scope_whitelist: list[str]) -> bool:
    """Return True when *target_host* is covered by at least one whitelist entry."""
    return any(
        target_matches_scope_entry(target_host, entry)
        for entry in in_scope_whitelist
        if entry.strip()
    )


def is_target_in_scope(target_host: str, in_scope_whitelist: list[str], out_of_scope_blacklist: list[str]) -> bool:
    """Return True when *target_host* is whitelisted and not blacklisted.

    Blacklist entries use the same matching rules, so a bare host, a wildcard
    subtree, or a CIDR range can each carve targets back out of scope. When a
    target matches both lists, the blacklist wins (the safe direction).
    """
    if not is_target_whitelisted(target_host, in_scope_whitelist):
        return False
    return not any(
        target_matches_scope_entry(target_host, entry)
        for entry in out_of_scope_blacklist
        if entry.strip()
    )

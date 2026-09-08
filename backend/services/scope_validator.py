import ipaddress
import re

def is_valid_target(target: str) -> bool:
    target = target.strip()
    if not target:
        return False
    try:
        ipaddress.ip_network(target, strict=False)
        return True
    except ValueError:
        pass
    return bool(re.match(r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-_]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}$", target) or target in ["localhost", "target.local", "juice-shop.local"])

def is_target_in_scope(target_host: str, in_scope_whitelist: list[str], out_of_scope_blacklist: list[str]) -> bool:
    target = target_host.strip().lower()
    blacklist = {s.strip().lower() for s in out_of_scope_blacklist if s.strip()}
    return target not in blacklist and target in {s.strip().lower() for s in in_scope_whitelist if s.strip()}

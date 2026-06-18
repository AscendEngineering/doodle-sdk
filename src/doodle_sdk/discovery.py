"""Auto-discovery of a Doodle Labs Mesh Rider radio on a local link.

A Mesh Rider radio sets a static IP in the 10.223.0.0/16 subnet. That IP is
derived from the radio's *wireless* MAC: the last two octets of the MAC become
the last two octets of the IP, in decimal. For example wireless MAC
``00:30:1A:4E:A4:3E`` -> ``10.223.164.62`` (0xA4 = 164, 0x3E = 62).

The companion computer never sees the wireless MAC directly. When the radio is
connected as a USB CDC-Ethernet gadget, the host-side interface reports the
gadget's ``host_addr`` MAC, which the radio firmware allocates sequentially from
its base MAC. The host-side MAC is a fixed +3 offset from the wireless MAC:

    :b9  (+0)  wireless MAC   <- the radio IP is derived from this
    :ba  (+1)  USB dev_addr   (radio's USB end)
    :bb  (+2)  (consumed elsewhere in the MAC block)
    :bc  (+3)  USB host_addr  <- what the host interface reports

So to recover the radio's IP from the host interface MAC we subtract the offset
(as a 48-bit MAC value, so a borrow propagates correctly into the 5th octet)
and then read the last two octets.
"""

import ipaddress
import socket

import psutil

# The subnet every Mesh Rider radio uses for its management IP.
DOODLE_SUBNET = ipaddress.ip_network("10.223.0.0/16")

# Fixed offset between the host-side USB-gadget MAC (what the companion reads)
# and the radio's wireless MAC (what the IP is derived from). See module docstring.
HOST_MAC_OFFSET = 3


def _mac_to_int(mac: str) -> int:
    """Parse a MAC string into its 48-bit integer value.

    Accepts colon- or hyphen-separated hex, upper or lower case.
    """
    cleaned = mac.replace(":", "").replace("-", "").strip()
    if len(cleaned) != 12:
        raise ValueError(f"Invalid MAC address: {mac!r}")
    return int(cleaned, 16)


def mac_to_radio_ip(mac: str, offset: int = HOST_MAC_OFFSET) -> str:
    """Derive a radio's 10.223.x.y management IP from a host-side interface MAC.

    Args:
        mac: MAC address of the local interface connected to the radio.
        offset: Amount to subtract from the MAC to recover the radio's wireless
            MAC. Defaults to the fixed Mesh Rider USB-gadget offset of 3.

    Returns:
        The derived radio IP as a string, e.g. "10.223.16.185".
    """
    wireless = _mac_to_int(mac) - offset
    x = (wireless >> 8) & 0xFF
    y = wireless & 0xFF
    return f"10.223.{x}.{y}"


def find_doodle_interface():
    """Find the local interface holding an IPv4 address in 10.223.0.0/16.

    Returns:
        A (interface_name, mac) tuple, or None if no matching interface exists.
    """
    if_addrs = psutil.net_if_addrs()
    for iface, addrs in if_addrs.items():
        has_doodle_ip = any(
            addr.family == socket.AF_INET
            and ipaddress.ip_address(addr.address) in DOODLE_SUBNET
            for addr in addrs
        )
        if not has_doodle_ip:
            continue

        mac = next(
            (addr.address for addr in addrs if addr.family == psutil.AF_LINK),
            None,
        )
        if mac:
            return iface, mac

    return None


def discover_radio_ip(offset: int = HOST_MAC_OFFSET):
    """Locate the Doodle interface and derive the radio's management IP.

    Returns:
        The derived radio IP string, or None if no Doodle interface is found.
    """
    found = find_doodle_interface()
    if not found:
        return None

    _iface, mac = found
    return mac_to_radio_ip(mac, offset)

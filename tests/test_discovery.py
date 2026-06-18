import ipaddress
import socket

import pytest

from doodle_sdk import discovery


# --- mac_to_radio_ip: core conversion ----------------------------------------

def test_known_radio():
    # Host-side MAC ...:bc -> wireless ...:b9 -> 10.223.16.185
    assert discovery.mac_to_radio_ip("00:30:1a:3e:10:bc") == "10.223.16.185"


def test_doc_example():
    # Doodle docs: wireless MAC ...A4:3E -> 10.223.164.62. Host-side is +3.
    assert discovery.mac_to_radio_ip("00:30:1a:4e:a4:41") == "10.223.164.62"


def test_ticket_example_with_offset_zero():
    # Acceptance-criteria example uses a direct (offset 0) conversion:
    # MAC ...1A:2B -> 10.223.26.43.
    assert discovery.mac_to_radio_ip("aa:bb:cc:dd:1a:2b", offset=0) == "10.223.26.43"


def test_uppercase_and_hyphen_separators():
    assert discovery.mac_to_radio_ip("AA-BB-CC-DD-10-BC") == "10.223.16.185"


# --- edge cases: final octets 00:00 and FF:FF (offset 0 to isolate math) ------

def test_final_octets_zero():
    assert discovery.mac_to_radio_ip("00:00:00:00:00:00", offset=0) == "10.223.0.0"


def test_final_octets_max():
    assert discovery.mac_to_radio_ip("ff:ff:ff:ff:ff:ff", offset=0) == "10.223.255.255"


def test_borrow_propagates_into_fifth_octet():
    # Subtracting the offset underflows the last octet and borrows into the 5th.
    # ...11:01 - 3 = ...10:FE -> 10.223.16.254
    assert discovery.mac_to_radio_ip("00:30:1a:3e:11:01") == "10.223.16.254"


def test_invalid_mac_raises():
    with pytest.raises(ValueError):
        discovery.mac_to_radio_ip("not-a-mac")
    with pytest.raises(ValueError):
        discovery.mac_to_radio_ip("00:11:22:33:44")  # too short


# --- find_doodle_interface / discover_radio_ip --------------------------------

class _Addr:
    def __init__(self, family, address):
        self.family = family
        self.address = address


def _make_addrs(monkeypatch, mapping):
    monkeypatch.setattr(discovery.psutil, "net_if_addrs", lambda: mapping)


def test_find_interface_matches_doodle_subnet(monkeypatch):
    _make_addrs(monkeypatch, {
        "lo": [_Addr(socket.AF_INET, "127.0.0.1")],
        "eth0": [_Addr(socket.AF_INET, "192.168.1.50")],
        "eth1": [
            _Addr(socket.AF_INET, "10.223.0.1"),
            _Addr(discovery.psutil.AF_LINK, "00:30:1a:3e:10:bc"),
        ],
    })
    assert discovery.find_doodle_interface() == ("eth1", "00:30:1a:3e:10:bc")


def test_find_interface_none_when_no_match(monkeypatch):
    _make_addrs(monkeypatch, {
        "eth0": [_Addr(socket.AF_INET, "192.168.1.50")],
    })
    assert discovery.find_doodle_interface() is None


def test_discover_radio_ip_end_to_end(monkeypatch):
    _make_addrs(monkeypatch, {
        "eth1": [
            _Addr(socket.AF_INET, "10.223.0.1"),
            _Addr(discovery.psutil.AF_LINK, "00:30:1a:3e:10:bc"),
        ],
    })
    assert discovery.discover_radio_ip() == "10.223.16.185"


def test_discover_radio_ip_none_when_no_interface(monkeypatch):
    _make_addrs(monkeypatch, {"eth0": [_Addr(socket.AF_INET, "192.168.1.50")]})
    assert discovery.discover_radio_ip() is None

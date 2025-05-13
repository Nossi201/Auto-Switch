# src/views/ConfigPageAdd/MainTabStructure.py
"""Utility module that defines the complete tab structure for switch configuration.

This module provides consistent tab organization across different forms,
ensuring a cohesive user experience. It defines eight main configuration
categories with corresponding sub-panels for all switch features.
"""

from enum import Enum
from typing import Dict, List, Tuple

class TabCategory(Enum):
    """Main configuration categories for switches and ports."""
    BASIC = "Basic Settings"
    VLANS = "VLANs"
    SPANNING_TREE = "Spanning Tree"
    SECURITY = "Security"
    QOS = "QoS"
    MONITORING = "Monitoring"
    ADVANCED_L2 = "Advanced L2"
    SYSTEM = "System"

class FeatureGroup(Enum):
    """Sub-groups of features within each tab category."""
    # Basic Tab Groups
    IDENTIFICATION = "Identification"
    PHYSICAL = "Physical Layer"
    MANAGEMENT = "Management"
    DISCOVERY = "Discovery Protocols"

    # VLAN Tab Groups
    VLAN_CONFIG = "VLAN Configuration"
    VOICE_VLAN = "Voice VLAN"
    VLAN_MAPPING = "VLAN Mapping"
    VTP = "VTP Settings"

    # Spanning Tree Groups
    STP_MODE = "STP Mode & Priority"
    STP_TIMERS = "Timers"
    STP_PROTECTION = "Protection Features"
    MST_CONFIG = "MST Configuration"

    # Security Groups
    PORT_SECURITY = "Port Security"
    AUTH_METHODS = "Authentication Methods"
    DHCP_ARP = "DHCP & ARP Security"
    IP_SOURCE = "IP Source Guard"
    IPV6_SECURITY = "IPv6 Security"

    # QoS Groups
    QOS_GLOBAL = "Global QoS"
    QOS_TRUST = "Trust Settings"
    QOS_MARKING = "Marking & Classification"
    QOS_QUEUING = "Queuing & Scheduling"
    QOS_POLICING = "Policing & Shaping"

    # Monitoring Groups
    LOGGING = "Logging"
    SNMP = "SNMP"
    SPAN = "Port Mirroring (SPAN)"
    NETFLOW = "NetFlow/sFlow"
    ERRDISABLE = "Error Detection & Recovery"

    # Advanced Layer 2 Groups
    LAYER2_PROTOCOLS = "Layer 2 Protocols"
    STORM_CONTROL = "Storm Control"
    MAC_TABLE = "MAC Address Table"
    JUMBO_FRAMES = "Jumbo Frames & MTU"
    UDLD = "UDLD"

    # System Groups
    AUTHENTICATION = "Authentication"
    AAA = "AAA"
    RADIUS_TACACS = "RADIUS/TACACS+"
    POWER = "Power Management"
    MISC = "Miscellaneous"

# Tab structure definitions for different form types
SWITCH_TEMPLATE_TABS: Dict[TabCategory, List[FeatureGroup]] = {
    TabCategory.BASIC: [
        FeatureGroup.IDENTIFICATION,
        FeatureGroup.MANAGEMENT,
        FeatureGroup.DISCOVERY
    ],
    TabCategory.VLANS: [
        FeatureGroup.VLAN_CONFIG,
        FeatureGroup.VTP
    ],
    TabCategory.SPANNING_TREE: [
        FeatureGroup.STP_MODE,
        FeatureGroup.STP_TIMERS,
        FeatureGroup.STP_PROTECTION,
        FeatureGroup.MST_CONFIG
    ],
    TabCategory.SECURITY: [
        FeatureGroup.PORT_SECURITY,
        FeatureGroup.DHCP_ARP,
        FeatureGroup.IP_SOURCE
    ],
    TabCategory.QOS: [
        FeatureGroup.QOS_GLOBAL,
        FeatureGroup.QOS_TRUST,
        FeatureGroup.QOS_QUEUING
    ],
    TabCategory.MONITORING: [
        FeatureGroup.LOGGING,
        FeatureGroup.SNMP,
        FeatureGroup.SPAN,
        FeatureGroup.NETFLOW,
        FeatureGroup.ERRDISABLE
    ],
    TabCategory.ADVANCED_L2: [
        FeatureGroup.LAYER2_PROTOCOLS,
        FeatureGroup.MAC_TABLE,
        FeatureGroup.JUMBO_FRAMES,
        FeatureGroup.UDLD
    ],
    TabCategory.SYSTEM: [
        FeatureGroup.AUTHENTICATION,
        FeatureGroup.AAA,
        FeatureGroup.RADIUS_TACACS,
        FeatureGroup.POWER
    ]
}

ACCESS_TEMPLATE_TABS: Dict[TabCategory, List[FeatureGroup]] = {
    TabCategory.BASIC: [
        FeatureGroup.IDENTIFICATION,
        FeatureGroup.PHYSICAL,
        FeatureGroup.DISCOVERY
    ],
    TabCategory.VLANS: [
        FeatureGroup.VLAN_CONFIG,
        FeatureGroup.VOICE_VLAN
    ],
    TabCategory.SPANNING_TREE: [
        FeatureGroup.STP_PROTECTION
    ],
    TabCategory.SECURITY: [
        FeatureGroup.PORT_SECURITY,
        FeatureGroup.AUTH_METHODS,
        FeatureGroup.DHCP_ARP,
        FeatureGroup.IP_SOURCE,
        FeatureGroup.IPV6_SECURITY
    ],
    TabCategory.QOS: [
        FeatureGroup.QOS_TRUST,
        FeatureGroup.QOS_MARKING,
        FeatureGroup.QOS_POLICING
    ],
    TabCategory.MONITORING: [
        FeatureGroup.ERRDISABLE
    ],
    TabCategory.ADVANCED_L2: [
        FeatureGroup.STORM_CONTROL,
        FeatureGroup.UDLD
    ],
    TabCategory.SYSTEM: [
        FeatureGroup.POWER,
        FeatureGroup.MISC
    ]
}

TRUNK_TEMPLATE_TABS: Dict[TabCategory, List[FeatureGroup]] = {
    TabCategory.BASIC: [
        FeatureGroup.IDENTIFICATION,
        FeatureGroup.PHYSICAL
    ],
    TabCategory.VLANS: [
        FeatureGroup.VLAN_CONFIG
    ],
    TabCategory.SPANNING_TREE: [
        FeatureGroup.STP_PROTECTION
    ],
    TabCategory.SECURITY: [
        FeatureGroup.DHCP_ARP,
        FeatureGroup.IP_SOURCE
    ],
    TabCategory.QOS: [
        FeatureGroup.QOS_TRUST,
        FeatureGroup.QOS_POLICING
    ],
    TabCategory.MONITORING: [
        FeatureGroup.ERRDISABLE
    ],
    TabCategory.ADVANCED_L2: [
        FeatureGroup.STORM_CONTROL,
        FeatureGroup.UDLD
    ],
    TabCategory.SYSTEM: [
        FeatureGroup.MISC
    ]
}

# Helper function to get tab structure for a specific form type
def get_tab_structure(form_type: str) -> Dict[TabCategory, List[FeatureGroup]]:
    """Return the tab structure for the specified form type.

    Args:
        form_type: Type of form ("switch", "access", or "trunk")

    Returns:
        Dictionary mapping tab categories to feature groups
    """
    if form_type.lower() == "switch":
        return SWITCH_TEMPLATE_TABS
    elif form_type.lower() == "access":
        return ACCESS_TEMPLATE_TABS
    elif form_type.lower() == "trunk":
        return TRUNK_TEMPLATE_TABS
    else:
        raise ValueError(f"Unknown form type: {form_type}")
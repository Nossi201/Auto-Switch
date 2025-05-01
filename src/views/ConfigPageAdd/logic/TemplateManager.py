#src/views/ConfigPageAdd/logic/TemplateManager.py
"""Handles new template creation and naming."""

from src.models.templates.TrunkTemplate import TrunkTemplate

def generate_template_name(instance, existing_keys: list[str]) -> str:
    """Generate a unique name for a newly created template."""
    if isinstance(instance, TrunkTemplate):
        vid = instance.native_vlan or (instance.allowed_vlans[0] if instance.allowed_vlans else 0)
        base_name = f"TRUNK {vid}" if vid else "TRUNK"
    else:
        vid = getattr(instance, "vlan_id", None)
        base_name = f"VLAN {vid}" if vid else "Custom template"

    name = base_name
    idx = 1
    while name in existing_keys:
        idx += 1
        name = f"{base_name} ({idx})"

    return name

"""Manager to track interface → template assignment."""

class InterfaceAssignmentManager:
    """Keeps track of which interface is assigned to which template."""

    def __init__(self, interfaces: list[str], default_template: str):
        # mapping: interface_name -> template_name
        self.interface_map = {iface: default_template for iface in interfaces}

    def assign(self, interface: str, template: str) -> bool:
        """Assign interface to a new template. Returns True if changed."""
        if interface not in self.interface_map:
            return False
        self.interface_map[interface] = template
        return True

    def get_template(self, interface: str) -> str:
        """Get template assigned to interface."""
        return self.interface_map.get(interface, "")

    def get_interfaces_for_template(self, template: str) -> list[str]:
        """Get list of interfaces assigned to given template."""
        return [iface for iface, tpl in self.interface_map.items() if tpl == template]

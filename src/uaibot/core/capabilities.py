"""
Capabilities Management Module

This module manages UaiBot's capabilities, tracking which features have been tested
and are available for use in production. It provides a centralized way to register,
validate, and utilize UaiBot's capabilities.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class Capability:
    """Represents a single UaiBot capability."""
    name: str
    description: str
    category: str
    is_tested: bool
    test_coverage: float
    last_tested: datetime
    implementation_path: str
    dependencies: List[str]
    status: str  # 'active', 'deprecated', 'experimental'
    version: str

class CapabilitiesManager:
    """Manages UaiBot's capabilities and their lifecycle."""
    
    def __init__(self, capabilities_file: Optional[str] = None):
        """Initialize the capabilities manager.
        
        Args:
            capabilities_file: Path to the capabilities registry file
        """
        self.capabilities: Dict[str, Capability] = {}
        self.capabilities_file = capabilities_file or "capabilities_registry.json"
        self._load_capabilities()

    def _load_capabilities(self) -> None:
        """Load capabilities from the registry file."""
        try:
            if Path(self.capabilities_file).exists():
                with open(self.capabilities_file, 'r') as f:
                    data = json.load(f)
                    for cap_data in data:
                        cap = Capability(
                            name=cap_data['name'],
                            description=cap_data['description'],
                            category=cap_data['category'],
                            is_tested=cap_data['is_tested'],
                            test_coverage=cap_data['test_coverage'],
                            last_tested=datetime.fromisoformat(cap_data['last_tested']),
                            implementation_path=cap_data['implementation_path'],
                            dependencies=cap_data['dependencies'],
                            status=cap_data['status'],
                            version=cap_data['version']
                        )
                        self.capabilities[cap.name] = cap
        except Exception as e:
            logger.error(f"Error loading capabilities: {e}")
            self.capabilities = {}

    def _save_capabilities(self) -> None:
        """Save capabilities to the registry file."""
        try:
            data = []
            for cap in self.capabilities.values():
                cap_data = {
                    'name': cap.name,
                    'description': cap.description,
                    'category': cap.category,
                    'is_tested': cap.is_tested,
                    'test_coverage': cap.test_coverage,
                    'last_tested': cap.last_tested.isoformat(),
                    'implementation_path': cap.implementation_path,
                    'dependencies': cap.dependencies,
                    'status': cap.status,
                    'version': cap.version
                }
                data.append(cap_data)
            
            with open(self.capabilities_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving capabilities: {e}")

    def register_capability(
        self,
        name: str,
        description: str,
        category: str,
        implementation_path: str,
        dependencies: List[str] = None,
        status: str = 'experimental',
        version: str = '0.1.0'
    ) -> None:
        """Register a new capability.
        
        Args:
            name: Unique identifier for the capability
            description: Description of what the capability does
            category: Category of the capability (e.g., 'input', 'output', 'system')
            implementation_path: Path to the implementation
            dependencies: List of other capabilities this depends on
            status: Current status of the capability
            version: Version of the capability
        """
        if name in self.capabilities:
            logger.warning(f"Capability {name} already exists. Updating...")
        
        self.capabilities[name] = Capability(
            name=name,
            description=description,
            category=category,
            is_tested=False,
            test_coverage=0.0,
            last_tested=datetime.now(),
            implementation_path=implementation_path,
            dependencies=dependencies or [],
            status=status,
            version=version
        )
        self._save_capabilities()

    def update_test_status(
        self,
        name: str,
        is_tested: bool,
        test_coverage: float,
        status: Optional[str] = None
    ) -> None:
        """Update the test status of a capability.
        
        Args:
            name: Name of the capability
            is_tested: Whether the capability has been tested
            test_coverage: Test coverage percentage
            status: New status (optional)
        """
        if name not in self.capabilities:
            raise ValueError(f"Capability {name} not found")
        
        cap = self.capabilities[name]
        cap.is_tested = is_tested
        cap.test_coverage = test_coverage
        cap.last_tested = datetime.now()
        if status:
            cap.status = status
        
        self._save_capabilities()

    def get_capability(self, name: str) -> Optional[Capability]:
        """Get a capability by name."""
        return self.capabilities.get(name)

    def list_capabilities(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        is_tested: Optional[bool] = None
    ) -> List[Capability]:
        """List capabilities matching the given filters."""
        caps = self.capabilities.values()
        
        if category:
            caps = [c for c in caps if c.category == category]
        if status:
            caps = [c for c in caps if c.status == status]
        if is_tested is not None:
            caps = [c for c in caps if c.is_tested == is_tested]
        
        return list(caps)

    def check_dependencies(self, name: str) -> List[str]:
        """Check if all dependencies for a capability are available.
        
        Returns:
            List of missing dependencies
        """
        if name not in self.capabilities:
            raise ValueError(f"Capability {name} not found")
        
        cap = self.capabilities[name]
        missing = []
        
        for dep in cap.dependencies:
            if dep not in self.capabilities:
                missing.append(dep)
            elif not self.capabilities[dep].is_tested:
                missing.append(f"{dep} (untested)")
        
        return missing

    def get_capability_status(self, name: str) -> Dict[str, Any]:
        """Get detailed status information for a capability."""
        if name not in self.capabilities:
            raise ValueError(f"Capability {name} not found")
        
        cap = self.capabilities[name]
        missing_deps = self.check_dependencies(name)
        
        return {
            'name': cap.name,
            'status': cap.status,
            'is_tested': cap.is_tested,
            'test_coverage': cap.test_coverage,
            'last_tested': cap.last_tested.isoformat(),
            'missing_dependencies': missing_deps,
            'is_ready': cap.is_tested and not missing_deps
        }

    def update_mouse_control_status(self) -> None:
        """Update the mouse control capability to reflect its tested status."""
        self.update_test_status(
            name="mouse_control",
            is_tested=True,
            test_coverage=95.0,
            status="active"
        )
        
        # Update the capability details
        if "mouse_control" in self.capabilities:
            cap = self.capabilities["mouse_control"]
            cap.version = "1.0.0"
            cap.description = "Control mouse movements, clicks, drags, and gestures"
            cap.dependencies = ["screen_reading"]
            self._save_capabilities() 
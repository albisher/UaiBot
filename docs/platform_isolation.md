# Platform Isolation Strategy

## Overview

The platform isolation strategy ensures that platform-specific code is properly isolated and maintainable. This document outlines the approach and rules for handling platform-specific code in the Labeeb project.

## Directory Structure

```
src/app/core/platform_core/
├── common/
│   └── platform_interface.py    # Base interface for all platforms
├── macos/
│   └── macos_platform.py        # macOS-specific implementation
├── win32/
│   └── windows_platform.py      # Windows-specific implementation
├── linux/
│   └── linux_platform.py        # Linux-specific implementation
└── platform_factory.py          # Factory for creating platform instances
```

## Key Principles

1. **Interface-First Design**
   - All platform-specific code must implement the `PlatformInterface`
   - Common functionality is defined in the interface
   - Platform-specific implementations handle the details

2. **Directory Naming**
   - Use `macos` instead of `darwin` for better future compatibility
   - Use `win32` for Windows
   - Use `linux` for Linux distributions

3. **Code Isolation**
   - Platform detection code must be in `platform_core`
   - No platform-specific code outside `platform_core`
   - Use the platform factory to create platform instances

4. **Dependency Management**
   - Platform-specific dependencies are clearly marked in `requirements.txt`
   - Dependencies are installed only on the relevant platform

## Implementation Rules

1. **Platform Detection**
   - Use `sys.platform` for platform detection
   - Handle platform detection only in `platform_factory.py`
   - Never use platform detection in other modules

2. **Error Handling**
   - Handle platform-specific errors gracefully
   - Provide meaningful error messages
   - Log platform-specific issues appropriately

3. **Testing**
   - Test platform-specific code on each platform
   - Mock platform-specific functionality in tests
   - Include platform-specific test cases

4. **Documentation**
   - Document platform-specific features
   - Note platform limitations
   - Include platform-specific setup instructions

## Audit Checks

The project audit script (`scripts/audit_project.py`) performs the following checks:

1. **Directory Structure**
   - Verifies existence of platform-specific directories
   - Checks for required implementation files

2. **Code Isolation**
   - Detects platform detection code outside `platform_core`
   - Ensures proper use of platform factory

3. **Dependencies**
   - Verifies platform-specific dependencies
   - Checks for missing required packages

4. **Naming Consistency**
   - Ensures consistent platform naming
   - Checks for old project name references

## Best Practices

1. **Adding New Platforms**
   - Create new platform directory
   - Implement `PlatformInterface`
   - Update platform factory
   - Add platform-specific tests

2. **Modifying Platform Code**
   - Update interface if needed
   - Maintain backward compatibility
   - Update documentation
   - Run platform-specific tests

3. **Handling Platform Differences**
   - Use feature detection when possible
   - Provide fallback implementations
   - Document platform limitations

## Maintenance

1. **Regular Audits**
   - Run project audit regularly
   - Fix violations promptly
   - Update documentation

2. **Version Control**
   - Keep platform-specific changes isolated
   - Use clear commit messages
   - Tag platform-specific releases

3. **Continuous Integration**
   - Test on all supported platforms
   - Verify platform isolation
   - Check dependency management 
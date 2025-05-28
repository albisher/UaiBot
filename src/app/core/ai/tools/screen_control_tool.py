import logging
import pyautogui
import gettext
import locale
import os
from typing import Dict, Any, Tuple
from src.app.core.platform_core.platform_manager import PlatformManager
from src.app.core.ai.tool_base import BaseTool
from src.app.core.ai.a2a_protocol import A2AProtocol
from src.app.core.ai.mcp_protocol import MCPProtocol
from src.app.core.ai.smol_agent import SmolAgentProtocol
from datetime import datetime
import mss
import mss.tools
from PIL import Image

"""
Screen Control Tool for Labeeb

This module provides screen control and automation capabilities for the Labeeb AI agent.
It handles screen-related operations like taking screenshots, locating images on screen,
and managing screen dimensions across different platforms.

Key features:
- Cross-platform screen control (macOS, Windows, Ubuntu)
- Screenshot capture with optional region selection
- Image recognition and location detection
- Screen dimension management
- Platform-specific configuration
- Internationalization (i18n) support with RTL layout handling
- A2A, MCP, and SmolAgents compliance

See also:
- docs/features/screen_control.md for detailed usage examples
- app/platform_core/platform_manager.py for platform-specific implementations
- docs/architecture/tools.md for tool architecture overview
"""

logger = logging.getLogger(__name__)

class ScreenControlTool(BaseTool):
    name = "screen_control"
    description = "Tool for screen control and automation capabilities."

    def __init__(self, language_code: str = 'en'):
        super().__init__(name=self.name, description=self.description)
        self.platform_manager = PlatformManager()
        self.platform_info = self.platform_manager.get_platform_info()
        self.handlers = self.platform_manager.get_handlers()
        self._configure_platform()
        self._setup_translations(language_code)

    def _log_protocol_action(self, protocol_name, action, details=None):
        # TODO: Implement real protocol integration for A2A, MCP, SmolAgents
        logger.debug(f"[Protocol:{protocol_name}] Action: {action}, Details: {details}")

    def _setup_translations(self, language_code: str) -> None:
        """Setup translations and RTL support for the specified language"""
        try:
            # Set locale for the current thread
            locale.setlocale(locale.LC_ALL, f'{language_code}.UTF-8')
            
            # Setup gettext translations
            self.translations = gettext.translation(
                'labeeb',
                localedir='locales',
                languages=[language_code],
                fallback=True
            )
            self._ = self.translations.gettext
            
            # Check if language is RTL
            self.is_rtl = language_code.startswith('ar')
            
            logger.info(f"Translations setup for language: {language_code} (RTL: {self.is_rtl})")
        except Exception as e:
            logger.error(f"Error setting up translations: {str(e)}")
            # Fallback to English
            self._ = lambda x: x
            self.is_rtl = False

    def _configure_platform(self) -> None:
        """Configure platform-specific screen settings"""
        try:
            platform_name = self.platform_info.get('name') or self.platform_info.get('platform') or 'unknown'
            if platform_name == 'mac':
                pyautogui.FAILSAFE = True
                pyautogui.PAUSE = 0.1
            elif platform_name == 'windows':
                pyautogui.FAILSAFE = True
                pyautogui.PAUSE = 0.1
            elif platform_name == 'ubuntu':
                pyautogui.FAILSAFE = True
                pyautogui.PAUSE = 0.1
        except Exception as e:
            logger.error(f"Error configuring platform: {str(e)}")

    async def get_screen_size(self) -> Dict[str, Any]:
        """Get screen size"""
        try:
            self._log_protocol_action('A2A', 'get_screen_size')
            self._log_protocol_action('MCP', 'get_screen_size')
            width, height = pyautogui.size()
            platform_name = self.platform_info.get('name') or self.platform_info.get('platform') or 'unknown'
            result = {
                'platform': platform_name,
                'action': 'get_size',
                'status': 'success',
                'size': {'width': width, 'height': height},
                'is_rtl': self.is_rtl
            }
            self._log_protocol_action('SmolAgents', 'get_screen_size', result)
            return result
        except Exception as e:
            error_msg = self._("Error getting screen size: {}").format(str(e))
            self._log_protocol_action('A2A', 'get_screen_size_error', error_msg)
            logger.error(error_msg)
            platform_name = self.platform_info.get('name') or self.platform_info.get('platform') or 'unknown'
            return {
                'platform': platform_name,
                'action': 'get_size',
                'status': 'error',
                'error': error_msg,
                'is_rtl': self.is_rtl
            }

    async def take_screenshot(self, region: Tuple[int, int, int, int] = None) -> Dict[str, Any]:
        """Take a screenshot using pyautogui for compatibility with Wayland and most Linux desktops."""
        try:
            self._log_protocol_action('A2A', 'take_screenshot', {'region': region})
            self._log_protocol_action('MCP', 'take_screenshot', {'region': region})
            platform_name = self.platform_info.get('name') or self.platform_info.get('platform') or 'unknown'
            result = {
                'platform': platform_name,
                'action': 'screenshot',
                'status': 'success',
                'image': None,
                'is_rtl': self.is_rtl
            }

            import pyautogui
            screenshot = pyautogui.screenshot(region=region)
            result['image'] = screenshot
            result['message'] = self._("Screen capture successful (pyautogui)")
            self._log_protocol_action('SmolAgents', 'take_screenshot', result)
            return result
        except Exception as e:
            error_msg = self._("Screen capture failed: {} (pyautogui)").format(str(e))
            self._log_protocol_action('A2A', 'take_screenshot_error', error_msg)
            logger.error(error_msg)
            platform_name = self.platform_info.get('name') or self.platform_info.get('platform') or 'unknown'
            return {
                'platform': platform_name,
                'action': 'screenshot',
                'status': 'error',
                'error': error_msg,
                'is_rtl': self.is_rtl
            }

    async def locate_on_screen(self, image_path: str, confidence: float = 0.9) -> Dict[str, Any]:
        """Locate an image on screen"""
        try:
            self._log_protocol_action('A2A', 'locate_on_screen', {'image_path': image_path, 'confidence': confidence})
            self._log_protocol_action('MCP', 'locate_on_screen', {'image_path': image_path, 'confidence': confidence})
            platform_name = self.platform_info.get('name') or self.platform_info.get('platform') or 'unknown'
            result = {
                'platform': platform_name,
                'action': 'locate',
                'status': 'success',
                'location': None,
                'is_rtl': self.is_rtl
            }

            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                result['location'] = {
                    'left': location.left,
                    'top': location.top,
                    'width': location.width,
                    'height': location.height
                }
                result['message'] = self._("Image found on screen")
            else:
                result['message'] = self._("Image not found on screen")
            self._log_protocol_action('SmolAgents', 'locate_on_screen', result)
            return result

        except Exception as e:
            error_msg = self._("Error locating image: {}").format(str(e))
            self._log_protocol_action('A2A', 'locate_on_screen_error', error_msg)
            logger.error(error_msg)
            platform_name = self.platform_info.get('name') or self.platform_info.get('platform') or 'unknown'
            return {
                'platform': platform_name,
                'action': 'locate',
                'status': 'error',
                'error': error_msg,
                'is_rtl': self.is_rtl
            }

    async def check_screen_availability(self) -> bool:
        """Check if screen control is available"""
        try:
            self._log_protocol_action('A2A', 'check_screen_availability')
            self._log_protocol_action('MCP', 'check_screen_availability')
            pyautogui.size()
            self._log_protocol_action('SmolAgents', 'check_screen_availability', {'available': True})
            return True
        except Exception as e:
            error_msg = self._("Error checking screen availability: {}").format(str(e))
            self._log_protocol_action('A2A', 'check_screen_availability_error', error_msg)
            logger.error(error_msg)
            return False

    # A2A Protocol Methods
    async def register_agent(self, agent_id: str, capabilities: Dict[str, Any]) -> None:
        await self.a2a_protocol.register_agent(agent_id, capabilities)

    async def unregister_agent(self, agent_id: str) -> None:
        await self.a2a_protocol.unregister_agent(agent_id)

    # MCP Protocol Methods
    async def register_channel(self, channel_id: str, channel_type: str) -> None:
        await self.mcp_protocol.register_channel(channel_id, channel_type)

    async def unregister_channel(self, channel_id: str) -> None:
        await self.mcp_protocol.unregister_channel(channel_id)

    # SmolAgent Protocol Methods
    async def register_capability(self, capability: str, handler: callable) -> None:
        await self.smol_protocol.register_capability(capability, handler)

    async def unregister_capability(self, capability: str) -> None:
        await self.smol_protocol.unregister_capability(capability)

    async def _execute_command(self, action: str, args: dict = None) -> dict:
        args = args or {}
        if action == 'take_screenshot':
            filename = args.get('filename')
            region = args.get('region')
            if not filename:
                # Default path and name
                folder = 'labeeb_tool_tests/صور_الشاشة'
                os.makedirs(folder, exist_ok=True)
                dt = datetime.now().strftime('%Y%m%d-%H%M%S')
                filename = os.path.join(folder, f'screenshot-{dt}.png')
            result = await self.take_screenshot(region=region)
            if result.get('image') is not None:
                result['image'].save(filename)
                result['saved_to'] = filename
            return result
        elif action == 'get_screen_size':
            return await self.get_screen_size()
        elif action == 'locate_on_screen':
            image_path = args.get('image_path')
            confidence = args.get('confidence', 0.9)
            return await self.locate_on_screen(image_path, confidence)
        else:
            return {'error': f'Unknown action: {action}'} 
import logging
from typing import Dict, Any, Optional
from labeeb.platform_core.platform_manager import PlatformManager

logger = logging.getLogger(__name__)

class OutputStyleManager:
    def __init__(self):
        self.platform_manager = PlatformManager()
        self.platform_info = self.platform_manager.get_platform_info()
        self.handlers = self.platform_manager.get_handlers()
        self.styles = self._init_styles()

    def _init_styles(self) -> Dict[str, Any]:
        """Initialize platform-specific styles"""
        base_styles = {
            'colors': {
                'primary': '#007AFF',
                'secondary': '#5856D6',
                'success': '#34C759',
                'warning': '#FF9500',
                'error': '#FF3B30',
                'info': '#5AC8FA',
                'background': '#FFFFFF',
                'text': '#000000'
            },
            'fonts': {
                'primary': 'System',
                'secondary': 'System',
                'monospace': 'Monaco'
            },
            'spacing': {
                'small': '4px',
                'medium': '8px',
                'large': '16px'
            },
            'borders': {
                'radius': '4px',
                'width': '1px',
                'color': '#E5E5EA'
            }
        }

        # Add platform-specific styles
        if self.platform_info['name'] == 'mac':
            base_styles.update({
                'colors': {
                    'primary': '#007AFF',
                    'secondary': '#5856D6',
                    'success': '#34C759',
                    'warning': '#FF9500',
                    'error': '#FF3B30',
                    'info': '#5AC8FA',
                    'background': '#FFFFFF',
                    'text': '#000000'
                },
                'fonts': {
                    'primary': 'SF Pro',
                    'secondary': 'SF Pro Text',
                    'monospace': 'SF Mono'
                }
            })
        elif self.platform_info['name'] == 'windows':
            base_styles.update({
                'colors': {
                    'primary': '#0078D4',
                    'secondary': '#2B88D8',
                    'success': '#107C10',
                    'warning': '#FFB900',
                    'error': '#D13438',
                    'info': '#00BCF2',
                    'background': '#FFFFFF',
                    'text': '#000000'
                },
                'fonts': {
                    'primary': 'Segoe UI',
                    'secondary': 'Segoe UI',
                    'monospace': 'Consolas'
                }
            })
        elif self.platform_info['name'] == 'ubuntu':
            base_styles.update({
                'colors': {
                    'primary': '#E95420',
                    'secondary': '#772953',
                    'success': '#38B44A',
                    'warning': '#EFB73E',
                    'error': '#DF382C',
                    'info': '#19B6EE',
                    'background': '#FFFFFF',
                    'text': '#000000'
                },
                'fonts': {
                    'primary': 'Ubuntu',
                    'secondary': 'Ubuntu',
                    'monospace': 'Ubuntu Mono'
                }
            })

        return base_styles

    def get_style(self, style_name: str) -> Optional[Any]:
        """Get a specific style by name"""
        try:
            return self.styles.get(style_name)
        except Exception as e:
            logger.error(f"Error getting style {style_name}: {str(e)}")
            return None

    def update_style(self, style_name: str, value: Any) -> bool:
        """Update a specific style"""
        try:
            if style_name in self.styles:
                self.styles[style_name] = value
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating style {style_name}: {str(e)}")
            return False

    def get_all_styles(self) -> Dict[str, Any]:
        """Get all styles"""
        return self.styles.copy()

    def reset_styles(self) -> None:
        """Reset styles to default"""
        self.styles = self._init_styles() 
import json
import logging
from typing import Tuple, Dict, Any, Optional

logger = logging.getLogger(__name__)

class AICommandExtractor:
    """Extracts commands from AI model responses."""
    
    def extract_command(self, response: str) -> Tuple[bool, Optional[Dict[str, Any]], Dict[str, Any]]:
        """
        Extract command from AI model response.
        
        Args:
            response: The AI model response text
            
        Returns:
            Tuple containing:
            - bool: Success status
            - Optional[Dict]: Command plan if successful
            - Dict: Metadata about the extraction
        """
        try:
            # Try to parse the response as JSON
            response_data = json.loads(response)
            
            # Validate the response structure
            if not isinstance(response_data, dict) or 'plan' not in response_data:
                return False, None, {
                    'error_message': 'Invalid response format: missing plan',
                    'response': response
                }
            
            plan = response_data['plan']
            if not isinstance(plan, list):
                return False, None, {
                    'error_message': 'Invalid plan format: not a list',
                    'response': response
                }
            
            # Validate each step in the plan
            for step in plan:
                if not isinstance(step, dict):
                    return False, None, {
                        'error_message': 'Invalid step format: not a dictionary',
                        'response': response
                    }
                
                required_fields = ['step', 'description', 'operation', 'parameters']
                for field in required_fields:
                    if field not in step:
                        return False, None, {
                            'error_message': f'Invalid step format: missing {field}',
                            'response': response
                        }
            
            return True, response_data, {
                'steps': len(plan),
                'response': response
            }
            
        except json.JSONDecodeError:
            return False, None, {
                'error_message': 'Failed to parse response as JSON',
                'response': response
            }
        except Exception as e:
            logger.error(f"Error extracting command: {str(e)}")
            return False, None, {
                'error_message': f'Error extracting command: {str(e)}',
                'response': response
            } 
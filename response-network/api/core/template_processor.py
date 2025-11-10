from typing import Dict, Any
import re
from fastapi import HTTPException, status


class TemplateProcessor:
    def __init__(self):
        self.placeholder_pattern = re.compile(r'\{\{([^}]+)\}\}')

    def extract_placeholders(self, template: str) -> set:
        """Extract all placeholders from a template string."""
        return set(self.placeholder_pattern.findall(template))

    def validate_template(self, template: Dict[str, Any], parameters: Dict[str, Any]) -> None:
        """
        Validate that all required placeholders are present in parameters.
        
        Args:
            template: The query template (can be nested dictionary)
            parameters: The parameters provided by the user
            
        Raises:
            HTTPException: If any required placeholder is missing
        """
        # Convert template to string to find all placeholders
        template_str = str(template)
        required_placeholders = self.extract_placeholders(template_str)
        
        missing_placeholders = required_placeholders - set(parameters.keys())
        if missing_placeholders:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required parameters: {', '.join(missing_placeholders)}"
            )

    def replace_placeholders(self, template: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Replace all placeholders in the template with actual values.
        
        Args:
            template: The query template (can be nested dictionary)
            parameters: The parameters to use for replacement
            
        Returns:
            Dict with placeholders replaced by actual values
        """
        # First validate that all required parameters are present
        self.validate_template(template, parameters)
        
        # Convert template to string, replace placeholders, and convert back to dict
        template_str = str(template)
        for key, value in parameters.items():
            template_str = template_str.replace('{{' + key + '}}', str(value))
            
        # Convert string back to dict (safely evaluate the string)
        # Note: In production, you might want to use a more robust solution
        # like traversing the original dict and replacing values
        try:
            return eval(template_str)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error processing template. Please check template format."
            )
# Step 5: Examples — mitreattack-python 2.0.0 documentation

**URL:** [https://mitreattack-python.readthedocs.io/en/latest/mitre_attack_data/examples.html](https://mitreattack-python.readthedocs.io/en/latest/mitre_attack_data/examples.html)

**Extracted Content:**

Examples — mitreattack-python 2.0.0 documentation
mitreattack-python
latest
Overview
Installation
Related MITRE Work
Contributing
Notice
MITRE ATT&CK Data Library
MitreAttackData
Examples
Getting An ATT&CK Object
Getting ATT&CK Objects by Type
Getting Multiple ATT&CK Objects
Related Objects
Custom Objects
Additional Modules
navlayers
attackToExcel
collections
diffStix
mitreattack-python
Examples
Edit on GitHub
Examples

The following are links to scripts of examples on how to use the
MitreAttackData
library. See the
examples
directory in the repository for more details.
Getting An ATT&CK Object

get_object_by_stix_id.py
get_object_by_attack_id.py
get_object_by_name.py
get_group_by_alias.py
get_software_by_alias.py
get_stix_type.py
get_attack_id.py
get_name.py
Getting ATT&CK Objects by Type

get_all_matrices.py
get_all_tactics.py
get_all_techniques.py
get_all_mitigations.py
get_all_groups.py
get_all_software.py
get_all_campaigns.py
get_all_datasources.py
get_all_datacomponents.py
Getting Multiple ATT&CK Objects

get_tactics_by_matrix.py
get_techniques_by_tactic.py
get_techniques_by_platform.py
get_objects_by_content.py
get_objects_created_after.py
Related Objects

Technique:Group Relationships
get_all_groups_using_all_techniques.py
get_groups_using_technique.py
get_all_techniques_used_by_all_groups.py
get_techniques_used_by_group.py
get_techniques_used_by_group_software.py
Technique:Campaign Relationships
get_all_techniques_used_by_all_campaigns.py
get_techniques_used_by_campaign.py
get_all_campaigns_using_all_techniques.py
get_campaigns_using_technique.py
Technique:Software Relationships
get_all_techniques_used_by_all_software.py
get_techniques_used_by_software.py
get_all_software_using_all_techniques.py
get_software_using_technique.py
Technique:Mitigation Relationships
get_all_techniques_mitigated_by_all_mitigations.py
get_techniques_mitigated_by_mitigation.py
get_all_mitigations_mitigating_all_techniques.py
get_mitigations_mitigating_technique.py
Technique:Su

**AI Analysis:**

{
  "plan": [
    {
      "step": "1",
      "description": "Analyze the provided content for relevant information about MITRE ATT&CK Framework.",
      "operation": "read_content",
      "parameters": {},
      "confidence": 0.0
    },
    {
      "step": "2",
      "description": "Identify key concepts and relationships within the content.",
      "operation": "read_content",
      "parameters": {},
      "confidence": 0.0
    },
    {
      "step": "3",
      "description": "Determine the primary focus of the content \u2013 is it a tutorial, a reference, or something else?",
      "operation": "analyze_content",
      "parameters": {},
      "confidence": 0.0
    },
    {
      "step": "4",
      "description": "Based on the content, determine the most relevant aspects to explore.",
      "operation": "assess_content",
      "parameters": {},
      "confidence": 0.0
    },
    {
      "step": "5",
      "description": "Create a plan to address the identified key aspects.",
      "operation": "plan_action",
      "parameters": {},
      "confidence": 0.0
    },
    {
      "step": "6",
      "description": "Execute the plan to achieve the desired outcome.",
      "operation": "execute_plan",
      "parameters": {},
      "confidence": 0.0
    }
  ]
}


# Research Log for python library


## Step 1: [mitreattack-python library — mitreattack-python 2.0.0 documentation](https://mitreattack-python.readthedocs.io/en/latest/index.html)

**URL:** [https://mitreattack-python.readthedocs.io/en/latest/index.html](https://mitreattack-python.readthedocs.io/en/latest/index.html)

**Extracted Content:**

mitreattack-python library — mitreattack-python 2.0.0 documentation
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
Custom Objects
Additional Modules
navlayers
attackToExcel
collections
diffStix
mitreattack-python
mitreattack-python library
Edit on GitHub
mitreattack-python library

mitreattack-python
is a library of Python tools and utilities for working with ATT&CK
content.
The main content of this library is in
MitreAttackData
; you can read more about
other modules in this library under “Additional Modules”.
Overview
Installation
Related MITRE Work
Contributing
Notice
MITRE ATT&CK Data Library
MitreAttackData
Examples
Custom Objects
Additional Modules
navlayers
attackToExcel
collections
diffStix
Next
© Copyright 2022, The MITRE Corporation.
Revision
688e6214
.
Built with
Sphinx
using a
theme
provided by
Read the Docs
.

**Links on Page:**

- [Installation](installation.html)
- [Related MITRE Work](related_work.html)
- [Contributing](contributing.html)
- [Notice](notice.html)
- [MitreAttackData](mitre_attack_data/mitre_attack_data.html)
- [Examples](mitre_attack_data/examples.html)
- [Custom Objects](mitre_attack_data/custom_objects.html)
- [navlayers](additional_modules/navlayers.html)
- [attackToExcel](additional_modules/attackToExcel.html)
- [collections](additional_modules/collections.html)
- [diffStix](additional_modules/diffStix.html)
- [Edit on GitHub](https://github.com/mitre-attack/mitreattack-python/blob/master/docs/index.rst)
- [MitreAttackData](mitre_attack_data/mitre_attack_data.html#mitreattackdata-ref)
- [Installation](installation.html)
- [Related MITRE Work](related_work.html)
- [Contributing](contributing.html)
- [Notice](notice.html)
- [MitreAttackData](mitre_attack_data/mitre_attack_data.html)
- [Examples](mitre_attack_data/examples.html)
- [Custom Objects](mitre_attack_data/custom_objects.html)
- [navlayers](additional_modules/navlayers.html)
- [attackToExcel](additional_modules/attackToExcel.html)
- [collections](additional_modules/collections.html)
- [diffStix](additional_modules/diffStix.html)
- [Next](installation.html)
- [Sphinx](https://www.sphinx-doc.org/)
- [theme](https://github.com/readthedocs/sphinx_rtd_theme)
- [Read the Docs](https://readthedocs.org)

**AI Analysis:**

{
  "command": "json\n{\n  \"plan\": [\n    {\n      \"step\": \"1\",\n      \"description\": \"Analyze the provided content to understand the library's purpose and functionality.\",\n      \"operation\": \"read_content\",\n      \"parameters\": {},\n      \"confidence\": 0.0\n    },\n    {\n      \"step\": \"2\",\n      \"description\": \"Identify key sections of the content related to the library's purpose and functionality.\",\n      \"operation\": \"read_content\",\n      \"parameters\": {},\n      \"confidence\": 0.0\n    },\n    {\n      \"step\": \"3\",\n      \"description\": \"Extract the library's main purpose and key features from the content.\",\n      \"operation\": \"extract_summary\",\n      \"parameters\": {\"summary\": \"The MITRE ATT&CK Data Library is a Python library for working with ATT&CK data. It provides tools and utilities for reading, processing, and utilizing ATT&CK data formats.\",\n      \"confidence\": 0.75}\n    },\n    {\n      \"step\": \"4\",\n      \"description\": \"Determine if the content provides sufficient detail to understand the library's functionality.\",\n      \"operation\": \"evaluate_content\",\n      \"parameters\": {\"content\": \"The content provides a good overview of the library's purpose and key features.\",\n      \"confidence\": 0.9\n    },\n    {\n      \"step\": \"5\",\n      \"description\": \"Identify missing information or areas for improvement.\",\n      \"operation\": \"identify_missing\",\n      \"parameters\": {\"missing_information\": \"The content lacks details on specific functionalities or usage examples.  More detailed examples would be beneficial.\",\n      \"confidence\": 0.8\n    },\n    {\n      \"step\": \"6\",\n      \"description\": \"Suggest potential next actions based on the identified missing information.\",\n      \"operation\": \"suggest_actions\",\n      \"parameters\": {\"actions\": [\"create_example\", \"generate_documentation\", \"search_for_specific_module\"]},\n      \"confidence\": 0.6\n    }\n  ]\n}",
  "type": "shell"
}


## Step 2: [Examples — mitreattack-python 2.0.0 documentation](https://mitreattack-python.readthedocs.io/en/latest/mitre_attack_data/examples.html)

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

**Links on Page:**

- [mitreattack-python](../index.html)
- [Installation](../installation.html)
- [Related MITRE Work](../related_work.html)
- [Contributing](../contributing.html)
- [Notice](../notice.html)
- [MitreAttackData](mitre_attack_data.html)
- [Custom Objects](custom_objects.html)
- [navlayers](../additional_modules/navlayers.html)
- [attackToExcel](../additional_modules/attackToExcel.html)
- [collections](../additional_modules/collections.html)
- [diffStix](../additional_modules/diffStix.html)
- [mitreattack-python](../index.html)
- [../index.html](../index.html)
- [Edit on GitHub](https://github.com/mitre-attack/mitreattack-python/blob/master/docs/mitre_attack_data/examples.rst)
- [examples](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/)
- [get_object_by_stix_id.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_object_by_stix_id.py)
- [get_object_by_attack_id.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_object_by_attack_id.py)
- [get_object_by_name.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_object_by_name.py)
- [get_group_by_alias.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_group_by_alias.py)
- [get_software_by_alias.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_software_by_alias.py)
- [get_stix_type.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_stix_type.py)
- [get_attack_id.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_attack_id.py)
- [get_name.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_name.py)
- [get_all_matrices.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_matrices.py)
- [get_all_tactics.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_tactics.py)
- [get_all_techniques.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_techniques.py)
- [get_all_mitigations.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_mitigations.py)
- [get_all_groups.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_groups.py)
- [get_all_software.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_software.py)
- [get_all_campaigns.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_campaigns.py)
- [get_all_datasources.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_datasources.py)
- [get_all_datacomponents.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_datacomponents.py)
- [get_tactics_by_matrix.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_tactics_by_matrix.py)
- [get_techniques_by_tactic.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_techniques_by_tactic.py)
- [get_techniques_by_platform.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_techniques_by_platform.py)
- [get_objects_by_content.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_objects_by_content.py)
- [get_objects_created_after.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_objects_created_after.py)
- [get_all_groups_using_all_techniques.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_groups_using_all_techniques.py)
- [get_groups_using_technique.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_groups_using_technique.py)
- [get_all_techniques_used_by_all_groups.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_techniques_used_by_all_groups.py)
- [get_techniques_used_by_group.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_techniques_used_by_group.py)
- [get_techniques_used_by_group_software.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_techniques_used_by_group_software.py)
- [get_all_techniques_used_by_all_campaigns.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_techniques_used_by_all_campaigns.py)
- [get_techniques_used_by_campaign.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_techniques_used_by_campaign.py)
- [get_all_campaigns_using_all_techniques.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_campaigns_using_all_techniques.py)
- [get_campaigns_using_technique.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_campaigns_using_technique.py)
- [get_all_techniques_used_by_all_software.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_techniques_used_by_all_software.py)
- [get_techniques_used_by_software.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_techniques_used_by_software.py)
- [get_all_software_using_all_techniques.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_software_using_all_techniques.py)
- [get_software_using_technique.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_software_using_technique.py)
- [get_all_techniques_mitigated_by_all_mitigations.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_techniques_mitigated_by_all_mitigations.py)
- [get_techniques_mitigated_by_mitigation.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_techniques_mitigated_by_mitigation.py)
- [get_all_mitigations_mitigating_all_techniques.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_mitigations_mitigating_all_techniques.py)
- [get_mitigations_mitigating_technique.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_mitigations_mitigating_technique.py)
- [get_all_parent_techniques_of_all_subtechniques.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_parent_techniques_of_all_subtechniques.py)
- [get_parent_technique_of_subtechnique.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_parent_technique_of_subtechnique.py)
- [get_all_subtechniques_of_all_techniques.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_subtechniques_of_all_techniques.py)
- [get_subtechniques_of_technique.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_subtechniques_of_technique.py)
- [get_all_datacomponents_detecting_all_techniques.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_datacomponents_detecting_all_techniques.py)
- [get_datacomponents_detecting_technique.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_datacomponents_detecting_technique.py)
- [get_all_techniques_detected_by_all_datacomponents.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_techniques_detected_by_all_datacomponents.py)
- [get_techniques_detected_by_datacomponent.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_techniques_detected_by_datacomponent.py)
- [get_all_groups_using_all_software.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_groups_using_all_software.py)
- [get_groups_using_software.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_groups_using_software.py)
- [get_all_software_used_by_all_groups.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_software_used_by_all_groups.py)
- [get_software_used_by_group.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_software_used_by_group.py)
- [get_all_campaigns_using_all_software.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_campaigns_using_all_software.py)
- [get_campaigns_using_software.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_campaigns_using_software.py)
- [get_all_software_used_by_all_campaigns.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_software_used_by_all_campaigns.py)
- [get_software_used_by_campaign.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_software_used_by_campaign.py)
- [get_all_groups_attributing_to_all_campaigns.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_groups_attributing_to_all_campaigns.py)
- [get_groups_attributing_to_campaign.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_groups_attributing_to_campaign.py)
- [get_all_campaigns_attributed_to_all_groups.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_all_campaigns_attributed_to_all_groups.py)
- [get_campaigns_attributed_to_group.py](https://github.com/mitre-attack/mitreattack-python/tree/master/examples/get_campaigns_attributed_to_group.py)
- [Previous](mitre_attack_data.html)
- [Next](custom_objects.html)
- [Sphinx](https://www.sphinx-doc.org/)
- [theme](https://github.com/readthedocs/sphinx_rtd_theme)
- [Read the Docs](https://readthedocs.org)

**AI Analysis:**

{
  "plan": [
    {
      "step": "1",
      "description": "Analyze the provided content to understand the topic of 'python library'.",
      "operation": "read_content",
      "parameters": {},
      "confidence": 0.0
    },
    {
      "step": "2",
      "description": "Identify key concepts and relationships within the content.",
      "operation": "parse_text",
      "parameters": {},
      "confidence": 0.0
    },
    {
      "step": "3",
      "description": "Determine the primary goal or purpose of the content.",
      "operation": "analyze_content",
      "parameters": {},
      "confidence": 0.0
    },
    {
      "step": "4",
      "description": "Based on the content, formulate a plan of action.  The plan should be focused on the content's purpose.",
      "operation": "plan_action",
      "parameters": {},
      "confidence": 0.0
    },
    {
      "step": "5",
      "description": "Execute the plan.  This will involve examining the links and content to understand the context.",
      "operation": "execute_plan",
      "parameters": {},
      "confidence": 0.0
    },
    {
      "step": "6",
      "description": "Assess the relevance and usefulness of the content for the topic.",
      "operation": "evaluate_content",
      "parameters": {},
      "confidence": 0.0
    },
    {
      "step": "7",
      "description": "Provide a concise summary of the content's key takeaways.",
      "operation": "generate_summary",
      "parameters": {},
      "confidence": 0.0
    },
    {
      "step": "8",
      "description": "Suggest potential next actions based on the content.",
      "operation": "suggest_next_actions",
      "parameters": {},
      "confidence": 0.0
    }
  ]
}


## Step 3: [diffStix — mitreattack-python 2.0.0 documentation](https://mitreattack-python.readthedocs.io/en/latest/additional_modules/diffStix.html)

**URL:** [https://mitreattack-python.readthedocs.io/en/latest/additional_modules/diffStix.html](https://mitreattack-python.readthedocs.io/en/latest/additional_modules/diffStix.html)

**Extracted Content:**

diffStix — mitreattack-python 2.0.0 documentation
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
Custom Objects
Additional Modules
navlayers
attackToExcel
collections
diffStix
mitreattack-python
diffStix
Edit on GitHub
diffStix

Create markdown, HTML, JSON and/or ATT&CK Navigator layers reporting on the changes between two
versions of the STIX2 bundles representing the ATT&CK content. Run ‘diff_stix -h’ for full usage
instructions.
Further documentation can be found
here
.
Previous
© Copyright 2022, The MITRE Corporation.
Revision
688e6214
.
Built with
Sphinx
using a
theme
provided by
Read the Docs
.

**Links on Page:**

- [mitreattack-python](../index.html)
- [Installation](../installation.html)
- [Related MITRE Work](../related_work.html)
- [Contributing](../contributing.html)
- [Notice](../notice.html)
- [MitreAttackData](../mitre_attack_data/mitre_attack_data.html)
- [Examples](../mitre_attack_data/examples.html)
- [Custom Objects](../mitre_attack_data/custom_objects.html)
- [navlayers](navlayers.html)
- [attackToExcel](attackToExcel.html)
- [collections](collections.html)
- [mitreattack-python](../index.html)
- [../index.html](../index.html)
- [Edit on GitHub](https://github.com/mitre-attack/mitreattack-python/blob/master/docs/additional_modules/diffStix.rst)
- [here](https://github.com/mitre-attack/mitreattack-python/tree/master/mitreattack/diffStix)
- [Previous](collections.html)
- [Sphinx](https://www.sphinx-doc.org/)
- [theme](https://github.com/readthedocs/sphinx_rtd_theme)
- [Read the Docs](https://readthedocs.org)

**AI Analysis:**

{
  "plan": [
    {
      "step": "1",
      "description": "Analyze the provided content to understand the topic of 'python library'.",
      "operation": "read_content",
      "parameters": {},
      "confidence": 0.0
    },
    {
      "step": "2",
      "description": "Identify key aspects of the content, such as the library's purpose, installation process, and documentation.",
      "operation": "read_content",
      "parameters": {},
      "confidence": 0.0
    },
    {
      "step": "3",
      "description": "Determine if the content is relevant to the topic of 'python library'.",
      "operation": "evaluate_relevance",
      "parameters": {
        "relevance": "high"
      },
      "confidence": 0.8
    },
    {
      "step": "4",
      "description": "Assess the comprehensiveness of the content. Does it provide sufficient detail?",
      "operation": "evaluate_comprehensiveness",
      "parameters": {
        "comprehensiveness": "medium"
      },
      "confidence": 0.7
    },
    {
      "step": "5",
      "description": "Identify missing information. What aspects of the library are not covered?",
      "operation": "identify_missing_information",
      "parameters": {},
      "confidence": 0.6
    },
    {
      "step": "6",
      "description": "Determine what actions are needed to proceed further with the topic.",
      "operation": "determine_next_actions",
      "parameters": {},
      "confidence": 0.9
    }
  ]
}


## Step 4: [navlayers — mitreattack-python 2.0.0 documentation](https://mitreattack-python.readthedocs.io/en/latest/additional_modules/navlayers.html)

**URL:** [https://mitreattack-python.readthedocs.io/en/latest/additional_modules/navlayers.html](https://mitreattack-python.readthedocs.io/en/latest/additional_modules/navlayers.html)

**Extracted Content:**

navlayers — mitreattack-python 2.0.0 documentation
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
Custom Objects
Additional Modules
navlayers
attackToExcel
collections
diffStix
mitreattack-python
navlayers
Edit on GitHub
navlayers

A collection of utilities for working with
ATT&CK Navigator
layers.
Provides the ability to import, export, and manipulate layers.
Layers can be read in from the filesystem or python dictionaries, combined and edited,
and then exported to excel or SVG images.
Further documentation can be found
here
.
Previous
Next
© Copyright 2022, The MITRE Corporation.
Revision
688e6214
.
Built with
Sphinx
using a
theme
provided by
Read the Docs
.

**Links on Page:**

- [mitreattack-python](../index.html)
- [Installation](../installation.html)
- [Related MITRE Work](../related_work.html)
- [Contributing](../contributing.html)
- [Notice](../notice.html)
- [MitreAttackData](../mitre_attack_data/mitre_attack_data.html)
- [Examples](../mitre_attack_data/examples.html)
- [Custom Objects](../mitre_attack_data/custom_objects.html)
- [attackToExcel](attackToExcel.html)
- [collections](collections.html)
- [diffStix](diffStix.html)
- [mitreattack-python](../index.html)
- [../index.html](../index.html)
- [Edit on GitHub](https://github.com/mitre-attack/mitreattack-python/blob/master/docs/additional_modules/navlayers.rst)
- [ATT&CK Navigator](https://github.com/mitre-attack/attack-navigator)
- [here](https://github.com/mitre-attack/mitreattack-python/tree/master/mitreattack/navlayers)
- [Previous](../mitre_attack_data/custom_objects.html)
- [Next](attackToExcel.html)
- [Sphinx](https://www.sphinx-doc.org/)
- [theme](https://github.com/readthedocs/sphinx_rtd_theme)
- [Read the Docs](https://readthedocs.org)

**AI Analysis:**

{
  "plan": [
    {
      "step": "1",
      "description": "Analyze the provided content to understand the topic of 'python library'.",
      "operation": "read_content",
      "parameters": {},
      "confidence": 0.0
    },
    {
      "step": "2",
      "description": "Extract key information from the content, focusing on the library's purpose and documentation.",
      "operation": "extract_key_info",
      "parameters": {
        "library_name": "navlayers"
      },
      "confidence": 0.7
    },
    {
      "step": "3",
      "description": "Determine if the content is relevant and comprehensive for the topic of 'python library'.",
      "operation": "assess_relevance",
      "parameters": {
        "relevance_score": 0.8
      },
      "confidence": 0.8
    },
    {
      "step": "4",
      "description": "Identify missing information and potential next actions based on the content.",
      "operation": "identify_missing_info",
      "parameters": {
        "missing_information": [
          "documentation structure",
          "installation process",
          "usage examples",
          "potential extensions",
          "dependencies"
        ]
      },
      "confidence": 0.6
    },
    {
      "step": "5",
      "description": "Generate a list of potential next actions based on the identified missing information.",
      "operation": "generate_actions",
      "parameters": {
        "actions": [
          "read_installation.html",
          "read_examples.html",
          "read_docs.rst",
          "create_example_file"
        ]
      },
      "confidence": 0.9
    }
  ]
}


## Step 5: [Contributing — mitreattack-python 2.0.0 documentation](https://mitreattack-python.readthedocs.io/en/latest/contributing.html)

**URL:** [https://mitreattack-python.readthedocs.io/en/latest/contributing.html](https://mitreattack-python.readthedocs.io/en/latest/contributing.html)

**Extracted Content:**

Contributing — mitreattack-python 2.0.0 documentation
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
Custom Objects
Additional Modules
navlayers
attackToExcel
collections
diffStix
mitreattack-python
Contributing
Edit on GitHub
Contributing

To contribute to this project, either through a bug report, feature request, or merge request,
please see the
Contributors Guide
.
Previous
Next
© Copyright 2022, The MITRE Corporation.
Revision
688e6214
.
Built with
Sphinx
using a
theme
provided by
Read the Docs
.

**Links on Page:**

- [mitreattack-python](index.html)
- [Installation](installation.html)
- [Related MITRE Work](related_work.html)
- [Notice](notice.html)
- [MitreAttackData](mitre_attack_data/mitre_attack_data.html)
- [Examples](mitre_attack_data/examples.html)
- [Custom Objects](mitre_attack_data/custom_objects.html)
- [navlayers](additional_modules/navlayers.html)
- [attackToExcel](additional_modules/attackToExcel.html)
- [collections](additional_modules/collections.html)
- [diffStix](additional_modules/diffStix.html)
- [mitreattack-python](index.html)
- [index.html](index.html)
- [Edit on GitHub](https://github.com/mitre-attack/mitreattack-python/blob/master/docs/contributing.rst)
- [Contributors Guide](https://github.com/mitre-attack/mitreattack-python/blob/master/docs/CONTRIBUTING.md)
- [Previous](related_work.html)
- [Next](notice.html)
- [Sphinx](https://www.sphinx-doc.org/)
- [theme](https://github.com/readthedocs/sphinx_rtd_theme)
- [Read the Docs](https://readthedocs.org)

**AI Analysis:**

{
  "command": "json\n{\n  \"plan\": [\n    {\n      \"step\": \"1\",\n      \"description\": \"Analyze the provided content to understand the purpose of the 'python library' topic.\",\n      \"operation\": \"read_content\",\n      \"parameters\": {},\n      \"confidence\": 0.0\n    },\n    {\n      \"step\": \"2\",\n      \"description\": \"Identify key sections within the content related to 'python library' \u2013 such as installation, documentation, examples, and contributing guidelines.\",\n      \"operation\": \"scan_content\",\n      \"parameters\": {\n        \"content\": \"mitreattack-python 2.0.0 documentation\"\n      },\n      \"confidence\": 0.6\n    },\n    {\n      \"step\": \"3\",\n      \"description\": \"Extract the 'Contributing' section and its related information.\",\n      \"operation\": \"extract_contributing\",\n      \"parameters\": {\n        \"content\": \"mitreattack-python 2.0.0 documentation\"\n      },\n      \"confidence\": 0.8\n    },\n    {\n      \"step\": \"4\",\n      \"description\": \"Understand the 'Contributing' section's instructions \u2013 specifically, the 'Contributing' section and the 'Edit on GitHub' link.\",\n      \"operation\": \"understand_contributing\",\n      \"parameters\": {\n        \"content\": \"mitreattack-python 2.0.0 documentation\"\n      },\n      \"confidence\": 0.9\n    },\n    {\n      \"step\": \"5\",\n      \"description\": \"Determine the next logical step \u2013 likely to review the 'related_work.html' and 'notice.html' links.\",\n      \"operation\": \"review_related_work\",\n      \"parameters\": {\n        \"content\": \"related_work.html\",\n        \"notice.html\"\n      },\n      \"confidence\": 0.7\n    },\n    {\n      \"step\": \"6\",\n      \"description\": \"Based on the content, determine if there's a need to follow the 'Previous' and 'Next' links.\",\n      \"operation\": \"follow_links\",\n      \"parameters\": {\n        \"content\": \"related_work.html\",\n        \"notice.html\"\n      },\n      \"confidence\": 0.85\n    }\n  ]\n}",
  "type": "shell"
}


## Step 6: [Installation — mitreattack-python 2.0.0 documentation](https://mitreattack-python.readthedocs.io/en/latest/installation.html)

**URL:** [https://mitreattack-python.readthedocs.io/en/latest/installation.html](https://mitreattack-python.readthedocs.io/en/latest/installation.html)

**Extracted Content:**

Installation — mitreattack-python 2.0.0 documentation
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
Custom Objects
Additional Modules
navlayers
attackToExcel
collections
diffStix
mitreattack-python
Installation
Edit on GitHub
Installation

To use this package, install the mitreattack-python library with
pip
:
pip
install
mitreattack-python
Note
: this library requires
python3
.
Previous
Next
© Copyright 2022, The MITRE Corporation.
Revision
688e6214
.
Built with
Sphinx
using a
theme
provided by
Read the Docs
.

**Links on Page:**

- [mitreattack-python](index.html)
- [Related MITRE Work](related_work.html)
- [Contributing](contributing.html)
- [Notice](notice.html)
- [MitreAttackData](mitre_attack_data/mitre_attack_data.html)
- [Examples](mitre_attack_data/examples.html)
- [Custom Objects](mitre_attack_data/custom_objects.html)
- [navlayers](additional_modules/navlayers.html)
- [attackToExcel](additional_modules/attackToExcel.html)
- [collections](additional_modules/collections.html)
- [diffStix](additional_modules/diffStix.html)
- [mitreattack-python](index.html)
- [index.html](index.html)
- [Edit on GitHub](https://github.com/mitre-attack/mitreattack-python/blob/master/docs/installation.rst)
- [pip](https://pip.pypa.io/en/stable/)
- [python3](https://www.python.org/)
- [Previous](index.html)
- [Next](related_work.html)
- [Sphinx](https://www.sphinx-doc.org/)
- [theme](https://github.com/readthedocs/sphinx_rtd_theme)
- [Read the Docs](https://readthedocs.org)

**AI Analysis:**

{
  "plan": [
    {
      "step": "1",
      "description": "Analyze the provided content to understand the library's purpose and potential use cases.",
      "operation": "read_and_understand",
      "parameters": {},
      "confidence": 0.0
    },
    {
      "step": "2",
      "description": "Identify key functionalities and potential dependencies within the library's documentation.",
      "operation": "read_documentation",
      "parameters": {},
      "confidence": 0.6
    },
    {
      "step": "3",
      "description": "Determine if the library is suitable for a research analysis task.  It seems to be related to data analysis and potentially cybersecurity.",
      "operation": "assess_suitability",
      "parameters": {
        "suitability": "high"
      },
      "confidence": 0.8
    },
    {
      "step": "4",
      "description": "Based on the content, suggest potential research questions or analysis areas.",
      "operation": "suggest_research_questions",
      "parameters": {},
      "confidence": 0.7
    },
    {
      "step": "5",
      "description": "If the research questions are relevant, suggest specific actions to gather more information.",
      "operation": "suggest_actions",
      "parameters": {},
      "confidence": 0.9
    }
  ]
}


## Step 7: [Custom Objects — mitreattack-python 2.0.0 documentation](https://mitreattack-python.readthedocs.io/en/latest/mitre_attack_data/custom_objects.html)

**URL:** [https://mitreattack-python.readthedocs.io/en/latest/mitre_attack_data/custom_objects.html](https://mitreattack-python.readthedocs.io/en/latest/mitre_attack_data/custom_objects.html)

**Extracted Content:**

Custom Objects — mitreattack-python 2.0.0 documentation
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
Custom Objects
Matrix
Tactic
DataSource
DataComponent
STIX Object Factory
stix20.StixObjectFactory()
Additional Modules
navlayers
attackToExcel
collections
diffStix
mitreattack-python
Custom Objects
Edit on GitHub
Custom Objects

Note
: This section includes nonessential information that is only relevant to users
who want a more advanced understanding of how this library is implemented.
ATT&CK uses a mix of predefined and custom STIX objects to implement ATT&CK concepts. More
information about the mapping of ATT&CK concepts to STIX 2.0 objects can be found in the the
ATT&CK Data Model documentation
. The
MitreAttackData
library implements the following
custom STIX object types
:
class
mitreattack.stix20.
Matrix
(
**
kwargs
)

Custom Properties:
tactic_refs
(
list[str]
) - The matrix array that contains an ordered list of
x-mitre-tactic
STIX IDs corresponding to the tactics of the matrix. The order of
tactic_refs
determines the order the tactics should appear within the matrix.
class
mitreattack.stix20.
Tactic
(
**
kwargs
)

Custom Properties:
x_mitre_shortname
(
str
) - The shortname of the tactic that is used for mapping
techniques to the tactic. This corresponds to the
kill_chain_phases.phase_name
of the techniques in the tactic.
class
mitreattack.stix20.
DataSource
(
**
kwargs
)

Custom Properties:
x_mitre_platforms
(
list[str]
) - The list of platforms that apply to the data source.
x_mitre_collection_layers
(
list[str]
) - The list of places the data can be
collected from.
class
mitreattack.stix20.
DataComponent
(
**
kwargs
)

Custom Properties:
x_mitre_data_source_ref
(
str
) - The STIX ID of the data source this component
is a part of.
STIX Object Factory

The return type of the
MitreAttackData
methods are determined by the StixObjectFactory method,
which convert

**Links on Page:**

- [mitreattack-python](../index.html)
- [Installation](../installation.html)
- [Related MITRE Work](../related_work.html)
- [Contributing](../contributing.html)
- [Notice](../notice.html)
- [MitreAttackData](mitre_attack_data.html)
- [Examples](examples.html)
- [navlayers](../additional_modules/navlayers.html)
- [attackToExcel](../additional_modules/attackToExcel.html)
- [collections](../additional_modules/collections.html)
- [diffStix](../additional_modules/diffStix.html)
- [mitreattack-python](../index.html)
- [../index.html](../index.html)
- [Edit on GitHub](https://github.com/mitre-attack/mitreattack-python/blob/master/docs/mitre_attack_data/custom_objects.rst)
- [ATT&CK Data Model documentation](https://github.com/mitre/cti/blob/ATT%26CK-v12.0/USAGE.md#the-attck-data-model)
- [custom STIX object types](https://stix2.readthedocs.io/en/latest/guide/custom.html#Custom-STIX-Object-Types)
- [STIX 2.0 Domain Object](https://stix2.readthedocs.io/en/latest/api/v20/stix2.v20.sdo.html#module-stix2.v20.sdo)
- [Previous](examples.html)
- [Next](../additional_modules/navlayers.html)
- [Sphinx](https://www.sphinx-doc.org/)
- [theme](https://github.com/readthedocs/sphinx_rtd_theme)
- [Read the Docs](https://readthedocs.org)

**AI Analysis:**

AI analysis failed.


## Step 8: [Notice — mitreattack-python 2.0.0 documentation](https://mitreattack-python.readthedocs.io/en/latest/notice.html)

**URL:** [https://mitreattack-python.readthedocs.io/en/latest/notice.html](https://mitreattack-python.readthedocs.io/en/latest/notice.html)

**Extracted Content:**

Notice — mitreattack-python 2.0.0 documentation
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
Custom Objects
Additional Modules
navlayers
attackToExcel
collections
diffStix
mitreattack-python
Notice
Edit on GitHub
Notice

Copyright 2022 The MITRE Corporation
Approved for Public Release; Distribution Unlimited. Case Number 19-0486.
Licensed under the Apache License, Version 2.0 (the “License”);
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an “AS IS” BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
This project makes use of ATT&CK®
ATT&CK Terms of Use
Previous
Next
© Copyright 2022, The MITRE Corporation.
Revision
688e6214
.
Built with
Sphinx
using a
theme
provided by
Read the Docs
.

**Links on Page:**

- [mitreattack-python](index.html)
- [Installation](installation.html)
- [Related MITRE Work](related_work.html)
- [Contributing](contributing.html)
- [MitreAttackData](mitre_attack_data/mitre_attack_data.html)
- [Examples](mitre_attack_data/examples.html)
- [Custom Objects](mitre_attack_data/custom_objects.html)
- [navlayers](additional_modules/navlayers.html)
- [attackToExcel](additional_modules/attackToExcel.html)
- [collections](additional_modules/collections.html)
- [diffStix](additional_modules/diffStix.html)
- [mitreattack-python](index.html)
- [index.html](index.html)
- [Edit on GitHub](https://github.com/mitre-attack/mitreattack-python/blob/master/docs/notice.rst)
- [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)
- [ATT&CK Terms of Use](https://attack.mitre.org/resources/terms-of-use/)
- [Previous](contributing.html)
- [Next](mitre_attack_data/mitre_attack_data.html)
- [Sphinx](https://www.sphinx-doc.org/)
- [theme](https://github.com/readthedocs/sphinx_rtd_theme)
- [Read the Docs](https://readthedocs.org)

**AI Analysis:**

{
  "command": "json\n{\n  \"plan\": [\n    {\n      \"step\": \"1\",\n      \"description\": \"Analyze the provided content to understand the topic of 'python library'.\",\n      \"operation\": \"read_content\",\n      \"parameters\": {},\n      \"confidence\": 0.0\n    },\n    {\n      \"step\": \"2\",\n      \"description\": \"Identify key information related to the 'python library' topic, focusing on documentation and examples.\",\n      \"operation\": \"read_content\",\n      \"parameters\": {},\n      \"confidence\": 0.5\n    },\n    {\n      \"step\": \"3\",\n      \"description\": \"Extract relevant information from the MITRE ATT&CK Data Library documentation, specifically focusing on the 'python library' section.\",\n      \"operation\": \"read_content\",\n      \"parameters\": {\n        \"content\": \"mitreattack-python 2.0.0 documentation\"\n      },\n      \"confidence\": 0.8\n    },\n    {\n      \"step\": \"4\",\n      \"description\": \"Summarize the key takeaways from the MITRE ATT&CK Data Library documentation regarding the 'python library'.\",\n      \"operation\": \"summarize\",\n      \"parameters\": {\n        \"content\": \"The MITRE ATT&CK Data Library provides documentation for the 'python library', including installation, related work, contributing, and examples. It highlights the library's use in ATT&CK data collection and analysis.\",\n      },\n      \"confidence\": 0.9\n    },\n    {\n      \"step\": \"5\",\n      \"description\": \"Generate a concise explanation of the 'python library' based on the extracted information.\",\n      \"operation\": \"generate_explanation\",\n      \"parameters\": {\n        \"content\": \"The 'python library' is a Python library used for data collection and analysis within the MITRE ATT&CK framework. It provides tools for creating custom objects, modules, and examples related to ATT&CK data.\"\n      },\n      \"confidence\": 0.75\n    },\n    {\n      \"step\": \"6\",\n      \"description\": \"Provide a brief overview of the library's functionality.\",\n      \"operation\": \"provide_overview\",\n      \"parameters\": {\n        \"content\": \"The 'python library' facilitates the creation of ATT&CK data, enabling users to collect and analyze data related to adversary tactics, techniques, and procedures (TTPs).\"\n      },\n      \"confidence\": 0.85\n    }\n  ]\n}",
  "type": "shell"
}


## Step 9: [Related MITRE Work — mitreattack-python 2.0.0 documentation](https://mitreattack-python.readthedocs.io/en/latest/related_work.html)

**URL:** [https://mitreattack-python.readthedocs.io/en/latest/related_work.html](https://mitreattack-python.readthedocs.io/en/latest/related_work.html)

**Extracted Content:**

Related MITRE Work — mitreattack-python 2.0.0 documentation
mitreattack-python
latest
Overview
Installation
Related MITRE Work
CTI
ATT&CK
STIX
Contributing
Notice
MITRE ATT&CK Data Library
MitreAttackData
Examples
Custom Objects
Additional Modules
navlayers
attackToExcel
collections
diffStix
mitreattack-python
Related MITRE Work
Edit on GitHub
Related MITRE Work

CTI

Cyber Threat Intelligence repository
of the ATT&CK catalog expressed in STIX 2.0 JSON. This
repository also contains
our USAGE document
which includes additional examples of accessing
and parsing our dataset in Python.
ATT&CK

ATT&CK® is a curated knowledge base and model for cyber adversary behavior, reflecting the various
phases of an adversary’s lifecycle, and the platforms they are known to target. ATT&CK is useful
for understanding security risk against known adversary behavior, for planning security
improvements, and verifying defenses work as expected.
https://attack.mitre.org
STIX

Structured Threat Information Expression
(STIX™) is a language and serialization format used to
exchange cyber threat intelligence (CTI).
STIX enables organizations to share CTI with one another in a consistent and machine-readable manner,
allowing security communities to better understand what computer-based attacks they are most likely to
see and to anticipate and/or respond to those attacks faster and more effectively.
STIX is designed to improve many capabilities, such as collaborative threat analysis, automated
threat exchange, automated detection and response, and more.
Previous
Next
© Copyright 2022, The MITRE Corporation.
Revision
688e6214
.
Built with
Sphinx
using a
theme
provided by
Read the Docs
.

**Links on Page:**

- [mitreattack-python](index.html)
- [Installation](installation.html)
- [Contributing](contributing.html)
- [Notice](notice.html)
- [MitreAttackData](mitre_attack_data/mitre_attack_data.html)
- [Examples](mitre_attack_data/examples.html)
- [Custom Objects](mitre_attack_data/custom_objects.html)
- [navlayers](additional_modules/navlayers.html)
- [attackToExcel](additional_modules/attackToExcel.html)
- [collections](additional_modules/collections.html)
- [diffStix](additional_modules/diffStix.html)
- [mitreattack-python](index.html)
- [index.html](index.html)
- [Edit on GitHub](https://github.com/mitre-attack/mitreattack-python/blob/master/docs/related_work.rst)
- [Cyber Threat Intelligence repository](https://github.com/mitre/cti)
- [our USAGE document](https://github.com/mitre/cti/blob/master/USAGE.md)
- [https://attack.mitre.org](https://attack.mitre.org)
- [Structured Threat Information Expression](https://oasis-open.github.io/cti-documentation/)
- [Previous](installation.html)
- [Next](contributing.html)
- [Sphinx](https://www.sphinx-doc.org/)
- [theme](https://github.com/readthedocs/sphinx_rtd_theme)
- [Read the Docs](https://readthedocs.org)

**AI Analysis:**

{
  "plan": [
    {
      "step": "1",
      "description": "Analyze the provided MITRE ATT&CK Data Library documentation to understand the key concepts and examples.",
      "operation": "read_documentation",
      "parameters": {},
      "confidence": 0.0
    },
    {
      "step": "2",
      "description": "Identify the core functionalities of the `mitreattack-python` library, focusing on its role in the ATT&CK framework.",
      "operation": "read_documentation",
      "parameters": {},
      "confidence": 0.0
    },
    {
      "step": "3",
      "description": "Determine if the library provides examples of custom objects and modules.",
      "operation": "read_documentation",
      "parameters": {},
      "confidence": 0.0
    },
    {
      "step": "4",
      "description": "Assess the library's integration with other MITRE Work items (CTI, ATT&CK, STIX).",
      "operation": "read_documentation",
      "parameters": {},
      "confidence": 0.0
    },
    {
      "step": "5",
      "description": "Evaluate the library's documentation and examples for potential use cases.",
      "operation": "read_documentation",
      "parameters": {},
      "confidence": 0.0
    },
    {
      "step": "6",
      "description": "If the library offers a clear and concise explanation of its usage, proceed to provide a basic example.",
      "operation": "create_example",
      "parameters": {},
      "confidence": 0.5
    }
  ]
}


## Step 10: [attackToExcel — mitreattack-python 2.0.0 documentation](https://mitreattack-python.readthedocs.io/en/latest/additional_modules/attackToExcel.html)

**URL:** [https://mitreattack-python.readthedocs.io/en/latest/additional_modules/attackToExcel.html](https://mitreattack-python.readthedocs.io/en/latest/additional_modules/attackToExcel.html)

**Extracted Content:**

attackToExcel — mitreattack-python 2.0.0 documentation
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
Custom Objects
Additional Modules
navlayers
attackToExcel
collections
diffStix
mitreattack-python
attackToExcel
Edit on GitHub
attackToExcel

A collection of utilities for converting
ATT&CK STIX data
to Excel spreadsheets.
It also provides access to
Pandas
DataFrames representing the dataset for use in data analysis.
Further documentation can be found
here
.
Previous
Next
© Copyright 2022, The MITRE Corporation.
Revision
688e6214
.
Built with
Sphinx
using a
theme
provided by
Read the Docs
.

**Links on Page:**

- [mitreattack-python](../index.html)
- [Installation](../installation.html)
- [Related MITRE Work](../related_work.html)
- [Contributing](../contributing.html)
- [Notice](../notice.html)
- [MitreAttackData](../mitre_attack_data/mitre_attack_data.html)
- [Examples](../mitre_attack_data/examples.html)
- [Custom Objects](../mitre_attack_data/custom_objects.html)
- [navlayers](navlayers.html)
- [collections](collections.html)
- [diffStix](diffStix.html)
- [mitreattack-python](../index.html)
- [../index.html](../index.html)
- [Edit on GitHub](https://github.com/mitre-attack/mitreattack-python/blob/master/docs/additional_modules/attackToExcel.rst)
- [ATT&CK STIX data](https://github.com/mitre/cti)
- [Pandas](https://pandas.pydata.org/)
- [here](https://github.com/mitre-attack/mitreattack-python/tree/master/mitreattack/attackToExcel)
- [Previous](navlayers.html)
- [Next](collections.html)
- [Sphinx](https://www.sphinx-doc.org/)
- [theme](https://github.com/readthedocs/sphinx_rtd_theme)
- [Read the Docs](https://readthedocs.org)

**AI Analysis:**

{
  "plan": [
    {
      "step": "1",
      "description": "Analyze the provided content to understand the topic of 'python library'.",
      "operation": "read_content",
      "parameters": {},
      "confidence": 0.0
    },
    {
      "step": "2",
      "description": "Identify key aspects of the content, such as the library's purpose, documentation, and related technologies.",
      "operation": "read_content",
      "parameters": {},
      "confidence": 0.0
    },
    {
      "step": "3",
      "description": "Determine if the content is relevant to the topic of 'python library'.",
      "operation": "evaluate_relevance",
      "parameters": {
        "relevance": "high"
      },
      "confidence": 0.8
    },
    {
      "step": "4",
      "description": "Assess the comprehensiveness of the content. Does it provide sufficient detail?",
      "operation": "evaluate_comprehensiveness",
      "parameters": {
        "comprehensiveness": "medium"
      },
      "confidence": 0.7
    },
    {
      "step": "5",
      "description": "Determine if the content is actionable. Can it be used to further research the topic?",
      "operation": "evaluate_actionability",
      "parameters": {
        "actionability": "high"
      },
      "confidence": 0.9
    },
    {
      "step": "6",
      "description": "Identify missing information. What is missing that would make this content more useful?",
      "operation": "identify_missing_info",
      "parameters": {},
      "confidence": 0.6
    },
    {
      "step": "7",
      "description": "Suggest potential next actions based on the identified missing information.",
      "operation": "generate_next_actions",
      "parameters": {},
      "confidence": 0.5
    }
  ]
}


## Step 11: [collections — mitreattack-python 2.0.0 documentation](https://mitreattack-python.readthedocs.io/en/latest/additional_modules/collections.html)

**URL:** [https://mitreattack-python.readthedocs.io/en/latest/additional_modules/collections.html](https://mitreattack-python.readthedocs.io/en/latest/additional_modules/collections.html)

**Extracted Content:**

collections — mitreattack-python 2.0.0 documentation
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
Custom Objects
Additional Modules
navlayers
attackToExcel
collections
diffStix
mitreattack-python
collections
Edit on GitHub
collections

A set of utilities for working with
ATT&CK Collections and Collection Indexes
.
Provides functionalities for converting and summarizing data in collections and collection indexes,
as well as generating a collection from a raw stix bundle input.
Further documentation can be found
here
.
Previous
Next
© Copyright 2022, The MITRE Corporation.
Revision
688e6214
.
Built with
Sphinx
using a
theme
provided by
Read the Docs
.

**Links on Page:**

- [mitreattack-python](../index.html)
- [Installation](../installation.html)
- [Related MITRE Work](../related_work.html)
- [Contributing](../contributing.html)
- [Notice](../notice.html)
- [MitreAttackData](../mitre_attack_data/mitre_attack_data.html)
- [Examples](../mitre_attack_data/examples.html)
- [Custom Objects](../mitre_attack_data/custom_objects.html)
- [navlayers](navlayers.html)
- [attackToExcel](attackToExcel.html)
- [diffStix](diffStix.html)
- [mitreattack-python](../index.html)
- [../index.html](../index.html)
- [Edit on GitHub](https://github.com/mitre-attack/mitreattack-python/blob/master/docs/additional_modules/collections.rst)
- [ATT&CK Collections and Collection Indexes](https://github.com/center-for-threat-informed-defense/attack-workbench-frontend/blob/master/docs/collections.md)
- [here](https://github.com/mitre-attack/mitreattack-python/tree/master/mitreattack/collections)
- [Previous](attackToExcel.html)
- [Next](diffStix.html)
- [Sphinx](https://www.sphinx-doc.org/)
- [theme](https://github.com/readthedocs/sphinx_rtd_theme)
- [Read the Docs](https://readthedocs.org)

**AI Analysis:**

{
  "plan": [
    {
      "step": "1",
      "description": "Analyze the provided content to understand the topic of 'python library'.",
      "operation": "read_content",
      "parameters": {},
      "confidence": 0.0
    },
    {
      "step": "2",
      "description": "Extract key information from the content, focusing on the library's purpose, documentation, and related concepts.",
      "operation": "extract_key_info",
      "parameters": {
        "focus": "python library functionality and documentation"
      },
      "confidence": 0.7
    },
    {
      "step": "3",
      "description": "Determine if the content is relevant and comprehensive for the topic. Assess the level of detail.",
      "operation": "assess_relevance",
      "parameters": {
        "relevance_score": 0.8
      },
      "confidence": 0.9
    },
    {
      "step": "4",
      "description": "Identify missing information and potential next actions based on the content.",
      "operation": "identify_missing_info",
      "parameters": {
        "missing_data": [
          "detailed documentation",
          "examples",
          "related MITRE work",
          "installation instructions",
          "usage examples"
        ]
      },
      "confidence": 0.6
    },
    {
      "step": "5",
      "description": "Generate a list of potential next actions based on the identified missing data.",
      "operation": "generate_actions",
      "parameters": {
        "actions": [
          "follow_link:<link_url>",
          "extract_table:<table_url>",
          "search:<keyword>"
        ]
      },
      "confidence": 0.85
    }
  ]
}


## Step 12: [MitreAttackData — mitreattack-python 2.0.0 documentation](https://mitreattack-python.readthedocs.io/en/latest/mitre_attack_data/mitre_attack_data.html)

**URL:** [https://mitreattack-python.readthedocs.io/en/latest/mitre_attack_data/mitre_attack_data.html](https://mitreattack-python.readthedocs.io/en/latest/mitre_attack_data/mitre_attack_data.html)

**Extracted Content:**

MitreAttackData — mitreattack-python 2.0.0 documentation
mitreattack-python
latest
Overview
Installation
Related MITRE Work
Contributing
Notice
MITRE ATT&CK Data Library
MitreAttackData
Usage
API Reference
MitreAttackData
MitreAttackData.get_all_campaigns_attributed_to_all_groups()
MitreAttackData.get_all_campaigns_using_all_software()
MitreAttackData.get_all_campaigns_using_all_techniques()
MitreAttackData.get_all_datacomponents_detecting_all_techniques()
MitreAttackData.get_all_groups_attributing_to_all_campaigns()
MitreAttackData.get_all_groups_using_all_software()
MitreAttackData.get_all_groups_using_all_techniques()
MitreAttackData.get_all_mitigations_mitigating_all_techniques()
MitreAttackData.get_all_parent_techniques_of_all_subtechniques()
MitreAttackData.get_all_software_used_by_all_campaigns()
MitreAttackData.get_all_software_used_by_all_groups()
MitreAttackData.get_all_software_using_all_techniques()
MitreAttackData.get_all_subtechniques_of_all_techniques()
MitreAttackData.get_all_techniques_detected_by_all_datacomponents()
MitreAttackData.get_all_techniques_mitigated_by_all_mitigations()
MitreAttackData.get_all_techniques_used_by_all_campaigns()
MitreAttackData.get_all_techniques_used_by_all_groups()
MitreAttackData.get_all_techniques_used_by_all_software()
MitreAttackData.get_attack_id()
MitreAttackData.get_campaigns()
MitreAttackData.get_campaigns_attributed_to_group()
MitreAttackData.get_campaigns_by_alias()
MitreAttackData.get_campaigns_using_software()
MitreAttackData.get_campaigns_using_technique()
MitreAttackData.get_datacomponents()
MitreAttackData.get_datacomponents_detecting_technique()
MitreAttackData.get_datasources()
MitreAttackData.get_groups()
MitreAttackData.get_groups_attributing_to_campaign()
MitreAttackData.get_groups_by_alias()
MitreAttackData.get_groups_using_software()
MitreAttackData.get_groups_using_technique()
MitreAttackData.get_matrices()
MitreAttackData.get_mitigations()
MitreAttackData.get_mitigations_mitigating_technique()
M

**Links on Page:**

- [mitreattack-python](../index.html)
- [Installation](../installation.html)
- [Related MITRE Work](../related_work.html)
- [Contributing](../contributing.html)
- [Notice](../notice.html)
- [Examples](examples.html)
- [Custom Objects](custom_objects.html)
- [navlayers](../additional_modules/navlayers.html)
- [attackToExcel](../additional_modules/attackToExcel.html)
- [collections](../additional_modules/collections.html)
- [diffStix](../additional_modules/diffStix.html)
- [mitreattack-python](../index.html)
- [../index.html](../index.html)
- [Edit on GitHub](https://github.com/mitre-attack/mitreattack-python/blob/master/docs/mitre_attack_data/mitre_attack_data.rst)
- [Enterprise ATT&CK](https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json)
- [Mobile ATT&CK](https://raw.githubusercontent.com/mitre/cti/master/mobile-attack/mobile-attack.json)
- [ATT&CK for ICS](https://raw.githubusercontent.com/mitre/cti/master/ics-attack/ics-attack.json)
- [Examples](examples.html#examples-ref)
- [STIX2 Python API Documentation](https://stix2.readthedocs.io/en/latest/)
- [ATT&CK Design and Philosophy Paper](https://attack.mitre.org/docs/ATTACK_Design_and_Philosophy_March_2020.pdf)
- [Previous](../notice.html)
- [Next](examples.html)
- [Sphinx](https://www.sphinx-doc.org/)
- [theme](https://github.com/readthedocs/sphinx_rtd_theme)
- [Read the Docs](https://readthedocs.org)

**AI Analysis:**

{
  "plan": [
    {
      "action": "follow_link",
      "url": "https://www.sphinx-doc.org/"
    },
    {
      "action": "extract_table",
      "url": "https://www.sphinx-doc.org/"
    },
    {
      "action": "search",
      "term": "mitreattack"
    }
  ],
  "confidence": 95
}


# Step 7: Custom Objects — mitreattack-python 2.0.0 documentation

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

**AI Analysis:**

AI analysis failed.


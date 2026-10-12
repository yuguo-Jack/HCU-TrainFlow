---
id: doc-yuguo-jack-hyperloom-6f4d1e72320ac1eaa03f
title: yuguo-Jack/Hyperloom / docs/_templates/autosummary/class.rst
engine: hyperloom
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: yuguo-Jack/Hyperloom
commit: 0425bde3f6e76e1588400c37d056dfd3bb75ac11
path: docs/_templates/autosummary/class.rst
raw_sha256: 00e6232a13e0422f21fc31b76d649c73067e676266e8228c5f27721f3c5d3930
sources: []
generated_body_sha256: 3d9e0a58ed58841a999de12aeb2f4f19c8e10facc8627433b67e965f24282155
source_state: current-scan
---

# yuguo-Jack/Hyperloom / docs/_templates/autosummary/class.rst

[Original at fixed commit](https://github.com/yuguo-Jack/Hyperloom/blob/0425bde3f6e76e1588400c37d056dfd3bb75ac11/docs/_templates/autosummary/class.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

{{ fullname | escape | underline }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :members:
   :show-inheritance:
   :inherited-members:

   {% block methods %}
   {% if methods %}
   .. rubric:: {{ _('Methods') }}

   .. autosummary::
   {% for item in methods %}
   {%- if item not in inherited_members %}
      ~{{ name }}.{{ item }}
   {%- endif %}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block attributes %}
   {% if attributes %}
   .. rubric:: {{ _('Attributes') }}

   .. autosummary::
   {% for item in attributes %}
      ~{{ name }}.{{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

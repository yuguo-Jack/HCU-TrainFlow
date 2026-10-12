---
id: doc-yuguo-jack-hyperloom-6729973033db42ee4f9f
title: yuguo-Jack/Hyperloom / docs/_templates/autosummary/module.rst
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
path: docs/_templates/autosummary/module.rst
raw_sha256: d64ad4717748c845a023759bbbb330e7ecb625962d394f8b0fd748ecee198641
sources: []
generated_body_sha256: c888f1ab7a42930562dcc34ffe02329badced82bc692e2d45bb75fdd110ae043
source_state: current-scan
---

# yuguo-Jack/Hyperloom / docs/_templates/autosummary/module.rst

[Original at fixed commit](https://github.com/yuguo-Jack/Hyperloom/blob/0425bde3f6e76e1588400c37d056dfd3bb75ac11/docs/_templates/autosummary/module.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

{{ fullname | escape | underline }}

.. automodule:: {{ fullname }}

   {% block attributes %}
   {% if attributes %}
   .. rubric:: Module Attributes

   .. autosummary::
   {% for item in attributes %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block functions %}
   {% if functions %}
   .. rubric:: {{ _('Functions') }}

   .. autosummary::
   {% for item in functions %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block classes %}
   {% if classes %}
   .. rubric:: {{ _('Classes') }}

   .. autosummary::
   {% for item in classes %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block exceptions %}
   {% if exceptions %}
   .. rubric:: {{ _('Exceptions') }}

   .. autosummary::
   {% for item in exceptions %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

{% block modules %}
{# Recurse into sub-modules, but skip test suites and example scripts so the
   API reference stays focused on the importable library surface. #}
{% set documented_modules = [] %}
{% for item in modules %}
{% set leaf = item.split('.')[-1] %}
{% if not leaf.startswith('test_') and leaf not in ['tests', 'examples', 'conftest'] %}
{{ documented_modules.append(item) or '' }}
{% endif %}
{% endfor %}
{% if documented_modules %}
.. rubric:: Modules

.. autosummary::
   :toctree:
   :recursive:
{% for item in documented_modules %}
   {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}

# {% if toc.title %}{{toc.title|safe}}{% else %}Untitled{% endif %}

By {{siteowner_name}} - [{% if 'www' not in site.domain %}www.{% endif %}{{site.domain}}](http://{% if 'www' not in site.domain %}www.{% endif %}{{site.domain}}/)  
*Date:  {{timestamp|date:'F j, Y'}}*

---

{% for page in pages %}
## {% if page.title %}{{page.title|safe}}{% else %}Untitled{% endif %}

{% load deertransform %}{% html_md page.body %}
{% endfor %}

--

(c) {{timestamp|date:'Y'}} {{siteowner_name}}  
*Original version and further downloads available at {{source_url}}*
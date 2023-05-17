# {% if page.title %}{{page.get_title|safe}}{% else %}Untitled{% endif %}

By {{sitemeta_author_name}} - [{% if 'www' not in site.domain %}www.{% endif %}{{site.domain}}](http://{% if 'www' not in site.domain %}www.{% endif %}{{site.domain}}/)  
*{{page.display_times.0.label}}:  {{page.display_times.0.timestamp|date:'F j, Y  G:i:s'}} | {{page.body|wordcount}} words*

---

{% load deertransform %}{% html_md body_text %}

--

(c) {{page.display_times.0.timestamp|date:'Y'}} {{sitemeta_author_name}}  
*Original version and further downloads available at http://{% if 'www' not in site.domain %}www.{% endif %}{{site.domain}}{% url 'page_htm' page.cat.cached_url page.slug %}*
# Lupinia Website (Awi)

Full website for Lupinia Studios, built with Django.  It's currently a work in progress.

Built by Natasha L. (@lupinia)

Domains
-------

- **[seneca.lupinia.net](http://seneca.lupinia.net/)** *(v5.1)* - Production server.  It runs the current stable version of this codebase at all times.
- **www.lupinia.net** *(v3.2)* - Deprecated production server; currently runs a legacy PHP version, and is a separate physical server from the other two.  For certain requests/URLs for features that are complete in 5.1, this server acts as a reverse proxy and passes requests to seneca.lupinia.net.

Apps/Modules Included
---------------------

Full feature list for these in-progress.

- **System/Structure**
	- **Awi Access**:  Unified access control, permissions, and ownership settings for any object.
	- **Awi Background**:  Dynamic background images for page body site-wide, with a tagging system to include/exclude certain images from certain categories and content items.
	- **Awi Error**:  Unified error text handling/template tags.
	- **DeerFind**:  Intelligent 404 handler.
- **Main Content**
	- **DeerTrees**:  Multi-level object-agnostic category system.
	- **DeerBooks**:  Enhanced text/writing management.
	- **DeerConnect**:  Link directory and contact information manager.
- **Other**
	- **DeerHealth**:  Prescription medication tracker.
	- **DeerFood**:  Restaurant-style menu system.
	- **secondlife**:  Legacy support for security/authentication scripts in Second Life.  Pending a rebuild, but unlike the others to be rebuilt, this one needs to stay running until it's replaced.

Third-Party Apps/Modules Used
-----------------------------

- **[Django Admin Tools](https://github.com/django-admin-tools/django-admin-tools)**:  Improvements to the Django administrative dashboard.
- **[Django Cookielaw](https://github.com/TyMaszWeb/django-cookie-law)**:  Easy tool for compliance with EU cookie law.
- **[Django Debug Toolbar](https://github.com/django-debug-toolbar/django-debug-toolbar)**:  Profiling and debugging tools for Django.  *(Dev only)*
- **[Django Honeypot](https://github.com/jamesturk/django-honeypot/)**:  Provides tools to reduce automated form spam.
- **[Django MPTT](https://github.com/django-mptt/django-mptt/)**:  Provides support for a recursive traversal tree structure; used for nested categories.
- **[Django MPTT Admin](https://github.com/mbraak/django-mptt-admin)**:  Enhanced administrative interface for objects using Django MPTT
- **[Django Processinfo](https://github.com/jedie/django-processinfo)**:  Basic server stats/health report.
- **[Django Static Precompiler](https://github.com/andreyfedoseev/django-static-precompiler)**:  Server-side compilation of CSS from SCSS.
- **[Django S3 Folder Storage](https://github.com/jamstooks/django-s3-folder-storage)**:  Adds Amazon S3 as a file storage provider, with the ability to use folders within the same bucket (instead of separate buckets for everything).
- **[Django Summernote](https://github.com/summernote/django-summernote)**:  WYSIWYG editor.
- **[HTML2Text](https://github.com/Alir3z4/html2text)**:  Library for converting HTML to Markdown.
- **[Rubber](https://launchpad.net/rubber/)**:  Utility for building documents from LaTeX source more easily.
- **[SassC](https://github.com/sass/sassc)**:  Library for processing CSS from SCSS.

Infrastructure
--------------

The site's current server uses Nginx as a front-end web server, uWSGI to serve its Django applications, and PostgreSQL Server 9.2 as a database back-end.  It also uses Amazon S3 for all static and media file hosting.

License
-------

This project is not licensed for re-use, but individual components of it may be licensed and distributed separately, including apps I've built.

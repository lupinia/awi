# Lupinia Website (Awi)

Full website for Lupinia Studios, built with Django.  It's currently a work in progress.

Built by Natasha L. (@lupinia)

Servers
-------

- **[seneca.lupinia.net](http://www.lupinia.net/)** *(v5.1)* - Production server.  It runs the current stable version of this codebase at all times.  All domains are primarily pointed at this server.
- **[allegheny.lupinia.net](http://allegheny.lupinia.net/)** *(v3.2)* - Deprecated former production server; currently runs the legacy PHP version of the Awi codebase, and it no longer handles production traffic, but some of its data has not yet been transferred to Seneca.

Apps/Modules Included
---------------------

- **System/Structure**
	- **Awi Access**:  Unified access control, permissions, and ownership settings for any object.
	- **Awi Background**:  Dynamic background images for page body site-wide, with a tagging system to include/exclude certain images from certain categories and content items.
	- **Awi Error**:  Unified error text handling/template tags.
	- **DeerFind**:  Intelligent 404 handler.
- **Main Content**
	- **DeerTrees**:  Multi-level object-agnostic category system.
	- **[DeerBooks](http://www.lupinia.net/code/projects/django/deerbooks.htm)**:  Enhanced text/writing management, with multi-format display (HTML, Markdown, Plain Text, LaTeX), and automatic generation of PDF, DVI, and PostScript files from dynamically-generated LaTeX source.
	- **DeerConnect**:  Link directory and contact information manager, with email form.
	- **[Sunset](http://www.lupinia.net/code/projects/django/sunset.htm)**:  Advanced image gallery, with built-in watermarking, metadata parsing, hash-based de-duplication, and batch imports from server-side directories.
- **Other**
	- **DeerHealth**:  Prescription medication tracker.
	- **DeerFood**:  Restaurant-style menu system.
	- **DeerCoins**:  Coin collection (numismatic) database and tools.
	- **secondlife**:  Legacy support for security/authentication scripts in Second Life.  Pending a rebuild, but unlike the others to be rebuilt, this one needs to stay running until it's replaced.

Third-Party Apps/Modules Used
-----------------------------

- **[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)**:  A Python library for parsing and manipulating HTML.
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
- **[ExifTool](http://www.sno.phy.queensu.ca/~phil/exiftool/)**:  Advanced metadata read/write tool.
- **[HTML2Text](https://github.com/Alir3z4/html2text)**:  Library for converting HTML to Markdown.
- **[JustifiedGallery](http://miromannino.github.io/Justified-Gallery/)**:  JQuery plugin for displaying a justified grid of mixed-width thumbnails.
- **[Leaflet](http://leafletjs.com/)**:  Map-display JavaScript library.
- **[MapBox](https://www.mapbox.com/)**:  Map data.
- **[Pillow](https://python-pillow.org/)**:  Upgraded fork of PIL (Python Imaging Library).
- **[PyExifTool](https://github.com/smarnach/pyexiftool)**:  Python wrapper for ExifTool.
- **[Rubber](https://launchpad.net/rubber/)**:  Utility for building documents from LaTeX source more easily.
- **[SassC](https://github.com/sass/sassc)**:  Library for processing CSS from SCSS.

Infrastructure
--------------

The site's current server uses Nginx as a front-end web server, uWSGI to serve its Django applications, and PostgreSQL Server 9.2 as a database back-end.  It also uses Amazon S3 for all static and media file hosting.

License
-------

This project is not licensed for re-use, but individual components of it may be licensed and distributed separately, including apps I've built.

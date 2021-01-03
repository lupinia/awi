# Lupinia Website (Awi)

Full website for Lupinia Studios, built with Django.  The site can be viewed at **[www.lupinia.net](http://www.lupinia.net/)**.

Built by Natasha L. (@lupinia)

Apps/Modules Included
---------------------

- **System/Structure**
	- **Awi Access**:  Unified access control, permissions, and ownership settings for any object.
	- **Awi Error**:  Unified error text handling/template tags.
	- **DeerFind**:  Intelligent 404 handler.
	- **UserTools**:  Extended user profiles and data used by multiple other apps/modules.
- **Main Content**
	- **[DeerTrees](http://www.lupinia.net/code/projects/django/deertrees.htm)**:  Multi-level object-agnostic category system.
	- **[DeerBooks](http://www.lupinia.net/code/projects/django/deerbooks.htm)**:  Enhanced text/writing management, with multi-format display (HTML, Markdown, Plain Text, LaTeX), and automatic generation of PDF, DVI, and PostScript files from dynamically-generated LaTeX source.
	- **DeerConnect**:  Link directory and contact information manager, with email form.
	- **[Sunset](http://www.lupinia.net/code/projects/django/sunset.htm)**:  Advanced image gallery, with built-in watermarking, metadata parsing, hash-based de-duplication, and batch imports from server-side directories.  Also provides dynamic background images for page body site-wide.
- **Second Life Systems/Content**
	- **DeerLand**:  Virtual world property/estate tracking and management.
	- **DeerGuard SL**:  Security/authentication system for LSL scripted systems in Second Life and other virtual worlds.
	- **secondlife**:  Legacy support for security/authentication scripts in Second Life.  Will be replaced by DeerGuard SL.
- **Other**
	- **Awi Utils**:  Miscellaneous core components used by multiple other modules/apps.
	- **DeerAttend**:  Event attendance history tracker/display.
	- **DeerHealth**:  Prescription medication tracker.
	- **DeerFood**:  Restaurant-style menu system.
	- **DeerCoins**:  Coin collection (numismatic) database and tools.

Third-Party Apps/Modules Used
-----------------------------

- **[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)**:  A Python library for parsing and manipulating HTML.
- **[Django Admin Tools](https://github.com/django-admin-tools/django-admin-tools)**:  Improvements to the Django administrative dashboard.
- **[Django Cookielaw](https://github.com/TyMaszWeb/django-cookie-law)**:  Easy tool for compliance with EU cookie law.
- **[Django Debug Toolbar](https://github.com/django-debug-toolbar/django-debug-toolbar)**:  Profiling and debugging tools for Django.  *(Dev only)*
- **[Django Haystack](https://github.com/django-haystack/django-haystack)**:  Powerful tool for integrating search indexing servers into Django.
- **[Django Honeypot](https://github.com/jamesturk/django-honeypot/)**:  Provides tools to reduce automated form spam.
- **[Django MPTT](https://github.com/django-mptt/django-mptt/)**:  Provides support for a recursive traversal tree structure; used for nested categories.
- **[Django MPTT Admin](https://github.com/mbraak/django-mptt-admin)**:  Enhanced administrative interface for objects using Django MPTT
- **[Django Static Precompiler](https://github.com/andreyfedoseev/django-static-precompiler)**:  Server-side compilation of CSS from SCSS.
- **[Django S3 Folder Storage](https://github.com/jamstooks/django-s3-folder-storage)**:  Adds Amazon S3 as a file storage provider, with the ability to use folders within the same bucket (instead of separate buckets for everything).
- **[ExifTool](http://www.sno.phy.queensu.ca/~phil/exiftool/)**:  Advanced metadata read/write tool.
- **[Highlight.js](https://highlightjs.org/)**:  Syntax highlighting for code displayed in HTML content.
- **[HTML2Text](https://github.com/Alir3z4/html2text)**:  Library for converting HTML to Markdown.
- **[JustifiedGallery](http://miromannino.github.io/Justified-Gallery/)**:  JQuery plugin for displaying a justified grid of mixed-width thumbnails.
- **[MapBox](https://www.mapbox.com/)**:  Map data.
- **[Pillow](https://python-pillow.org/)**:  Upgraded fork of PIL (Python Imaging Library).
- **[PyExifTool](https://github.com/smarnach/pyexiftool)**:  Python wrapper for ExifTool.
- **[Rubber](https://launchpad.net/rubber/)**:  Utility for building documents from LaTeX source more easily.
- **[SassC](https://github.com/sass/sassc)**:  Library for processing CSS from SCSS.

Infrastructure
--------------

- **Web Server**:  Nginx *(seneca.lupinia.net)*
- **WSGI Connector**:  uWSGI
- **Database Server**:  PostgreSQL *(Amazon RDS)*
- **Static/Media Hosting**:  Amazon S3 *(cdn.fur.vc)*
- **Search Indexing Server**:  Amazon ElasticSearch

Custom Management Commands
-------------------

- **process_images (Sunset):**  If images need their assets rebuilt, this will rebuild them in the background.  If not, it will check batch import folders for new images to import.
- **compile_latex (DeerBooks):**  If document files for a page need to be built/rebuilt, this will rebuild them in the background.
- **set_cat_thumb (DeerTrees):**  Set the thumbnail for categories containing images.
- **cleanup_working_dir (Awi Utils):**  Delete unused files from the local working directories for background processes that need to perform file manipulation (compile_latex, process_images).
- **health_check (DeerConnect)**:  Performs a HEAD request to every external link in the system, and notifies the administrator(s) if any links return a status other than 200.
- **promote_seasonal (Awi Utils):**  Selectively feature/unfeature certain categories based on the current month.
- **clearcache (Awi Utils):**  Clear Django's cache, something that Django really should have a built-in management command for.
- **no_export_deleted (DeerBooks):**  Sets auto_export to False on pages that have been moved to the "Trash" category, in case this wasn't already handled.

License
-------

This project as a whole is not currently licensed for re-use, but individual components of it may be licensed and distributed separately, including apps I've built.

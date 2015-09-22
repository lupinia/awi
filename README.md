# Lupinia Website (Awi)

Full website for Lupinia Studios, built with Django.  It's currently a work in progress.

Built by Natasha L. (@lupinia)

Domains
-------

- **beta.lupinia.net** *(v5.1)* - Dev server for this project, runs the latest version of this codebase at all times.
- **seneca.lupinia.net** *(v4.1)* - Pseudo-staging server; this will become the production server once the site is fully finished.  
	- *Current development goal is to bring v5.1 up to the same featureset as the incomplete v4.1, to upgrade Seneca.  New features will follow.*
- **www.lupinia.net** *(v3.2)* - Production server; currently runs a legacy PHP version, and is a separate physical server from the other two.

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
- **Other**
	- **DeerHealth**:  Prescription medication tracker.
	- **secondlife**:  Legacy support for security/authentication scripts in Second Life.  Pending a rebuild, but unlike the others to be rebuilt, this one needs to stay running until it's replaced.

Third-Party Apps/Modules Used
-----------------------------

- **[Django Admin Tools](https://github.com/django-admin-tools/django-admin-tools)**:  Improvements to the Django administrative dashboard.
- **[Django Debug Toolbar](https://github.com/django-debug-toolbar/django-debug-toolbar)**:  Profiling and debugging tools for Django.  *(Dev only)*
- **[Django MPTT](https://github.com/django-mptt/django-mptt/)**:  Provides support for a recursive traversal tree structure; used for nested categories.
- **[Django MPTT Admin](https://github.com/mbraak/django-mptt-admin)**:  Enhanced administrative interface for objects using Django MPTT
- **[Django Processinfo](https://github.com/jedie/django-processinfo)**:  Basic server stats/health report.
- **[Django S3 Folder Storage](https://github.com/jamstooks/django-s3-folder-storage)**:  Adds Amazon S3 as a file storage provider, with the ability to use folders within the same bucket (instead of separate buckets for everything).
- **[Django Summernote](https://github.com/summernote/django-summernote)**:  WYSIWYG editor.

Infrastructure
--------------

The site's current server uses Nginx as a front-end web server, uWSGI to serve its Django applications, and PostgreSQL Server 9.2 as a database back-end.  It also uses Amazon S3 for all static and media file hosting.

License
-------

This project is not licensed for re-use, but individual components of it may be licensed and distributed separately, including apps I've built.
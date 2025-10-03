# -*- coding: utf-8 -*-
{
    'name': "Library Base",
    'summary': """
        Core models for library management system: books, authors, publishers, branches and copies.""",
    'description': """
        Library Management Base Module
        ==============================

        This module provides the foundational models for a comprehensive library management system:

        Main Features:
        * **Authors Management**: Track book authors with biographical information
        * **Publishers Management**: Manage publishing companies and their details  
        * **Books Catalog**: Intellectual works independent of physical manifestations
        * **Editions Tracking**: Specific manifestations of works (ISBN, format, publisher)
        * **Physical Copies**: Individual trackable items in library inventory
        * **Branch Locations**: Multi-location library system support
        * **Genre Classification**: Hierarchical categorization system

        Technical Features:
        * Complete audit trails with mail.thread integration
        * Advanced search and filtering capabilities
        * Data validation and normalization
        * Multi-language support
        * REST API compatible data structures
        * Performance optimized with proper indexing
        * Comprehensive test coverage

        This is the base module that other library modules depend on:
        * library_management (loans, reservations, patrons)  
        * library_reports (analytics, reporting)
        * library_web (web interface customizations)
    """,
    'author': "json-dev",
    'website': "https://www.json-dev.com",
    'category': 'Resources Management',
    'version': '18.0.1.0.0',
    'depends': ['base', 'mail'],
    'data': [
        # Data
        'data/module_category_data.xml',    # 1
        
        # Security
        'security/library_security.xml',    # 2
        'security/ir.model.access.csv',     # 3

        # Views
        'views/author_views.xml',
        'views/publisher_views.xml',
        'views/genre_views.xml',
        'views/branch_views.xml',
        'views/book_views.xml',
        'views/edition_views.xml',
        'views/book_copy_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'test': [
        'tests/test_author.py',
        'tests/test_publisher.py',
        'tests/test_genre.py',
        'tests/test_branch.py',
        'tests/test_book.py',
        'tests/test_edition.py',
        'tests/test_book_copy.py',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

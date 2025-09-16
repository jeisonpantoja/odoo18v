# -*- coding: utf-8 -*-
{
    'name': 'library_base',
    'version': '1.0.0',
    'summary': 'Core models for Library (books, authors, publishers)',
    'description': """
Library base module: core models and basic access rules for a library.
Includes book, author and publisher models and the minimal security setup.
    """,
    'author': 'json-dev',
    'website': 'https://www.json-dev.com',
    'category': 'Extra Tools',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'account'],  
    'data': [
        'security/library_security.xml',        # groups (optional)
        'security/ir.model.access.csv',         # permissions
        # 'views/library_menu.xml',               # top-level menu and actions
        # 'views/library_book_views.xml',         # book form/tree views
        # 'views/library_author_views.xml',       # author views
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'assets': {
        'web.assets_backend': [
            # put here js/css for backend widgets if needed
            # 'library_base/static/src/js/library_widget.js',
            # 'library_base/static/src/css/library_styles.css',
        ],
    },
}

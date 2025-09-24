# Estructura Mejorada del Módulo library_base

```
library_base/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py           # Importa todos los modelos
│   ├── author.py            # Modelo library.author
│   ├── publisher.py         # Modelo library.publisher
│   ├── genre.py             # Modelo library.genre
│   ├── branch.py            # Modelo library.branch
│   ├── book.py              # Modelo library.book
│   ├── edition.py           # Modelo library.edition
│   └── book_copy.py         # Modelo library.book_copy
├── tests/
│   ├── __init__.py
│   ├── test_author.py       # Tests para author
│   ├── test_publisher.py    # Tests para publisher
│   ├── test_genre.py        # Tests para genre
│   ├── test_branch.py       # Tests para branch
│   ├── test_book.py         # Tests para book
│   ├── test_edition.py      # Tests para edition
│   └── test_book_copy.py    # Tests para book_copy
├── views/
│   ├── author_views.xml     # Vistas para author
│   ├── publisher_views.xml  # Vistas para publisher
│   ├── genre_views.xml      # Vistas para genre
│   ├── branch_views.xml     # Vistas para branch
│   ├── book_views.xml       # Vistas para book
│   ├── edition_views.xml    # Vistas para edition
│   └── book_copy_views.xml  # Vistas para book_copy
├── security/
│   ├── ir.model.access.csv
│   └── library_security.xml
├── data/
│   └── module_category_data.xml
└── demo/
    └── demo.xml
```

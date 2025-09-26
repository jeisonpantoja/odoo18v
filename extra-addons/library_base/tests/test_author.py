# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date


class TestLibraryAuthor(TransactionCase):
    """Test cases for library.author model following TDD methodology."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.Author = self.env['library.author']

        # Datos de prueba válidos
        self.valid_author_data = {
            'name': 'Gabriel García Márquez',
            'birth_date': date(1927, 3, 6),
            'death_date': date(2014, 4, 17),
            'country': 'Colombia',
            'biography': 'Premio Nobel de Literatura 1982'
        }

    # ============ PRIORIDAD ALTA - Tests Esenciales ============

    def test_create_author_minimal(self):
        """Test creating author with minimal required data."""
        # ARRANGE - preparar datos
        minimal_data = {'name': 'Miguel de Cervantes'}

        # ACT - ejecutar acción
        author = self.Author.create(minimal_data)

        # ASSERT - verificar resultados
        self.assertTrue(author.id, "Author should be created successfully")
        self.assertEqual(author.name, 'Miguel de Cervantes')
        self.assertTrue(author.active, "Author should be active by default")
        self.assertFalse(author.birth_date, "Birth date should be optional")

    def test_create_author_empty_name_fails(self):
        """Test that empty or whitespace-only names raise ValidationError."""
        # Test con nombre vacío
        with self.assertRaises(ValidationError) as context:
            self.Author.create({'name': ''})
        self.assertIn('Author name is required', str(context.exception))

        # Test con solo espacios
        with self.assertRaises(ValidationError) as context:
            self.Author.create({'name': '   '})
        self.assertIn('Author name is required', str(context.exception))

        # Test con None
        with self.assertRaises(ValidationError) as context:
            self.Author.create({'name': None})

    def test_birth_date_not_in_future(self):
        """Test that future birth dates are rejected."""
        future_date = date(2030, 1, 1)

        with self.assertRaises(ValidationError) as context:
            self.Author.create({
                'name': 'Future Author',
                'birth_date': future_date
            })
        self.assertIn('Birth date cannot be in the future',
                      str(context.exception))

    def test_death_before_birth_fails(self):
        """Test that death_date before birth_date raises ValidationError."""
        invalid_data = {
            'name': 'Invalid Author',
            'birth_date': date(2000, 1, 1),
            'death_date': date(1990, 1, 1)  # Muerte antes del nacimiento
        }

        with self.assertRaises(ValidationError) as context:
            self.Author.create(invalid_data)
        self.assertIn('Death date must be after birth date',
                      str(context.exception))

    # ============ PRIORIDAD MEDIA - Funcionalidad de Negocio ============

    def test_name_normalization_on_create(self):
        """Test that names are properly normalized (spaces trimmed/collapsed)."""
        # Test con espacios extra
        author = self.Author.create({'name': '  William   Shakespeare  '})
        self.assertEqual(author.name, 'William Shakespeare')

        # Test con múltiples espacios internos
        author2 = self.Author.create({'name': 'Charles    Dickens'})
        self.assertEqual(author2.name, 'Charles Dickens')

    def test_name_normalization_on_write(self):
        """Test that names are normalized on update."""
        author = self.Author.create({'name': 'Test Author'})
        author.write({'name': '  Updated   Name  '})
        self.assertEqual(author.name, 'Updated Name')

    def test_display_name_computation(self):
        """Test that display_name includes birth/death dates when available."""
        # Solo con año de nacimiento
        author1 = self.Author.create({
            'name': 'Living Author',
            'birth_date': date(1950, 5, 15)
        })
        self.assertEqual(author1.display_name, 'Living Author (1950)')

        # Con ambas fechas
        author2 = self.Author.create(self.valid_author_data)
        self.assertEqual(author2.display_name,
                         'Gabriel García Márquez (1927-2014)')

        # Sin fechas
        author3 = self.Author.create({'name': 'Anonymous Author'})
        self.assertEqual(author3.display_name, 'Anonymous Author')

    def test_as_dict_method(self):
        """Test that as_dict method returns correct dictionary."""
        author = self.Author.create(self.valid_author_data)

        # Test con campos por defecto
        result = author.as_dict()
        expected_fields = ['id', 'name', 'country', 'birth_date', 'death_date']
        for field in expected_fields:
            self.assertIn(field, result)

        # Test con campos específicos
        result = author.as_dict(['name', 'country'])
        self.assertEqual(set(result.keys()), {'name', 'country'})
        self.assertEqual(result['name'], 'Gabriel García Márquez')
        self.assertEqual(result['country'], 'Colombia')

    # ============ PRIORIDAD MEDIA - Relaciones ============

    def test_partner_id_optional(self):
        """Test that partner_id can be None or valid res.partner."""
        # Sin partner
        author = self.Author.create({'name': 'Author Without Partner'})
        self.assertFalse(author.partner_id)

        # Con partner válido
        partner = self.env['res.partner'].create({'name': 'Author Contact'})
        author_with_partner = self.Author.create({
            'name': 'Author With Partner',
            'partner_id': partner.id
        })
        self.assertEqual(author_with_partner.partner_id, partner)

    # ============ TESTS DE INTEGRACIÓN (se implementarán después) ============

    def test_get_books_method_placeholder(self):
        """Placeholder for testing get_books method - will implement when book model exists."""
        author = self.Author.create({'name': 'Test Author'})
        books = author.get_books()
        # Por ahora debe retornar recordset vacío
        self.assertEqual(len(books), 0)

    # ============ TESTS DE VALIDACIÓN AVANZADA ============

    def test_multiple_authors_same_name_allowed(self):
        """Test that multiple authors can have the same name (no uniqueness constraint)."""
        name = 'John Smith'
        author1 = self.Author.create({'name': name})
        author2 = self.Author.create({'name': name})

        self.assertNotEqual(author1.id, author2.id)
        self.assertEqual(author1.name, author2.name)

    def test_active_field_behavior(self):
        """Test that active field works correctly for archiving."""
        author = self.Author.create({'name': 'Test Author'})
        self.assertTrue(author.active)

        # Archivar autor
        author.write({'active': False})
        self.assertFalse(author.active)

        # Búsquedas normales no deberían encontrar autores archivados
        search_result = self.Author.search([('name', '=', 'Test Author')])
        self.assertEqual(len(search_result), 0)

        # Búsqueda explícita con active=False sí debería encontrarlo
        search_with_archived = self.Author.with_context(active_test=False).search([
            ('name', '=', 'Test Author')
        ])
        self.assertEqual(len(search_with_archived), 1)

    def test_constraint_validation_on_write(self):
        """Test that constraints are validated on write operations too."""
        author = self.Author.create({
            'name': 'Valid Author',
            'birth_date': date(1950, 1, 1)
        })

        # Intentar cambiar a fecha futura debe fallar
        with self.assertRaises(ValidationError):
            author.write({'birth_date': date(2030, 1, 1)})

    def test_mail_thread_integration(self):
        """Test that mail.thread integration works."""
        author = self.Author.create({'name': 'Test Author'})

        # Verificar que tiene capacidades de mensajería
        self.assertTrue(hasattr(author, 'message_post'))
        self.assertTrue(hasattr(author, 'message_ids'))

        # Test posting a message
        author.message_post(body='Test message', subject='Test Subject')
        self.assertTrue(len(author.message_ids) > 0)

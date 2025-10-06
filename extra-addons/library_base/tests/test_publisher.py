# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date


class TestLibraryPublisher(TransactionCase):
    """
    Test cases for library.publisher model following TDD methodology.

    TDD Phase 1: Focus on core functionality without external dependencies
    - Basic CRUD operations
    - Field validations
    - Data normalization
    - Computed fields (display_name)
    - API serialization methods
    """

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.Publisher = self.env['library.publisher']

        # Datos de prueba válidos
        self.valid_publisher_data = {
            'name': 'Penguin Random House',
            'website': 'https://www.penguinrandomhouse.com',
            'founded_year': 2013,
            'country': 'United States',
            'description': 'Global publishing company'
        }

    # ============ HIGH PRIORITY - Essentials test ============

    def test_create_publisher_minimal(self):
        """Test creating publisher with only required field (name)."""
        publisher = self.Publisher.create({'name': 'Test Publisher'})

        self.assertTrue(publisher.id)
        self.assertEqual(publisher.name, 'Test Publisher')
        self.assertTrue(publisher.active)

    def test_create_publisher_empty_name_fails(self):
        """Test that empty or whitespace-only names raise ValidationError."""
        with self.assertRaises(ValidationError) as context:
            self.Publisher.create({'name': ''})

        with self.assertRaises(ValidationError) as context:
            self.Publisher.create({'name': '   '})

    def test_founded_year_validation(self):
        """Test that founded_year must be reasonable (>= 1400 and <= current year)."""
        # Año muy antiguo (antes de la imprenta) debe fallar
        with self.assertRaises(ValidationError):
            self.Publisher.create({
                'name': 'Ancient Publisher',
                'founded_year': 1300
            })

        # Año futuro debe fallar
        with self.assertRaises(ValidationError):
            self.Publisher.create({
                'name': 'Future Publisher',
                'founded_year': 2100
            })

        # Año válido debe funcionar
        publisher = self.Publisher.create({
            'name': 'Valid Publisher',
            'founded_year': 2025
        })

        self.assertEqual(publisher.founded_year, 2025)

    def test_website_format_validation(self):
        """Test that website must start with 'http://' or 'https://'."""
        # Sin protocolo debe fallar
        with self.assertRaises(ValidationError):
            self.Publisher.create({
                'name': 'No Protocol Publisher',
                'website': 'www.example.com'
            })

        # Con http:// debe funcionar
        publisher1 = self.Publisher.create({
            'name': 'HTTP Publisher',
            'website': 'http://www.example.com'
        })

        self.assertTrue(publisher1.id)

        # Con https:// debe funcionar
        publisher2 = self.Publisher.create({
            'name': 'HTTPS Publisher',
            'website': 'https://www.example.com'
        })

        self.assertTrue(publisher2.id)

     # ============ MEDIA PRIORITY - Business logic ============

    def test_name_normalization_on_create(self):
        """Test that names are properly normalized (spaces trimmed/collapsed)."""
        publisher = self.Publisher.create({'name':   '  Oxford   University   Press  '})
        self.assertEqual(publisher.name, 'Oxford University Press')
        
    def test_name_normalization_on_write(self):
        """Test that names are normalized on update."""
        publisher = self.Publisher.create({'name': 'Test Publisher'})
        publisher.write({'name': '  Updated   Name  '})
        self.assertEqual(publisher.name, 'Updated Name')

    def test_as_dict_method(self):
        """Test that as_dict serialization method."""
        publisher = self.Publisher.create(self.valid_publisher_data)
        
        # Test con campos por defecto
        result = publisher.as_dict()
        expected_fields = ['id', 'name', 'website', 'founded_year', 'country']
        for field in expected_fields:
            self.assertIn(field, result)

        self.assertEqual(result['name'], 'Penguin Random House')
        self.assertEqual(result['country'], 'United States')

    # ============ RELATIONSHIPS ============
        
    def test_contact_id_optional(self):
        """Test that contact_id is optional."""
        publisher = self.Publisher.create({'name': 'No Contact Publisher'})
        self.assertFalse(publisher.contact_id)
        
        # Con contacto existente
        existing_partner = self.env['res.partner'].search([], limit=1)
        if existing_partner:
            publisher_with_contact = self.Publisher.create({
                'name': 'Publisher With Contact',
                'contact_id': existing_partner.id
            })
            self.assertEqual(publisher_with_contact.contact_id, existing_partner) 
            
    # ============ ADVANCED VALIDATION ============
    
    def test_multiple_publishers_same_name_allowed(self):
        """Test that duplicate names are allowed (no uniqueness constraint)."""
        name = 'Generic Publisher'
        publisher1 = self.Publisher.create({'name': name})
        publisher2 = self.Publisher.create({'name': name})

        self.assertNotEqual(publisher1.id, publisher2.id)
        self.assertEqual(publisher1.name, publisher2.name)
        
    def test_active_field_behavior(self):
        """Test archiving functionality."""
        publisher = self.Publisher.create({'name': 'Archive Publisher'})
        self.assertTrue(publisher.active)

        # Archivar
        publisher.write({'active': False})
        self.assertFalse(publisher.active)
        
        # Normal search shouldn't find archived
        search_result = self.Publisher.search([('name', '=', 'Archive Publisher')])
        self.assertEqual(len(search_result), 0)
        
        # Explicit search with active=False should find it
        search_with_archived = self.Publisher.with_context(active_test=False).search([
            ('name', '=', 'Archive Publisher')
        ])
        self.assertEqual(len(search_with_archived), 1)
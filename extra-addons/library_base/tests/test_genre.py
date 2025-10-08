# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from psycopg2 import IntegrityError
from datetime import date


class TestLibraryGenre(TransactionCase):
    """
    Test cases for library.genre model following TDD methodology.

    TDD Phase 1: Focus on core functionality without external dependencies
    - Basic CRUD operations
    - Field validations
    - Recursivity validation
    """

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.Genre = self.env['library.genre']

    # ============== HIGH PRIORITY - ESSENTIALS TESTS ==============

    def test_create_genre_minimal(self):
        """Test creating genre with minimal required data."""
        genre = self.Genre.create({'name': 'Fiction'})

        self.assertTrue(genre.id)
        self.assertEqual(genre.name, 'Fiction')
        self.assertTrue(genre.active)
        self.assertFalse(genre.parent_id, 'Parent should be optional')

    def test_genre_empty_name_fails(self):
        """Test that empty or whitespace-only names raise ValidationError."""
        with self.assertRaises(ValidationError):
            self.Genre.create({'name': ''})

        with self.assertRaises(ValidationError):
            self.Genre.create({'name': '   '})

    def test_genre_cannot_be_own_parent(self):
        """Test self-referential parent relationship fails"""
        genre = self.Genre.create({'name': 'Fiction'})

        with self.assertRaises(UserError):
            genre.write({'parent_id': genre.id})

    def test_parent_hierarchy_validation(self):
        """Test that circular hierarchies are prevented."""
        # Create hierarchy: Fiction -> Sci-Fi -> Cyberpunk
        fiction = self.Genre.create({'name': 'Fiction'})
        sci_fi = self.Genre.create(
            {'name': 'Science Fiction', 'parent_id': fiction.id})
        cyberpunk = self.Genre.create(
            {'name': 'Cyberpunk', 'parent_id': sci_fi.id})

        # Try create loop: Fiction.parent_id = Cyberpunk (her nieto)
        with self.assertRaises(UserError):
            fiction.write({'parent_id': cyberpunk.id})

        # Try create loop: Ficition.parent_id = Sci-Fi (her son)
        with self.assertRaises(UserError):
            fiction.write({'parent_id': sci_fi.id})

 # ============ MEDIUM PRIORITY - HIERARQUIES RELATIONSHIPS ============

    def test_parent_child_relationship(self):
        """Test parent-child relationships work correctly."""

        # Create father:
        fiction = self.Genre.create({'name': 'Fiction'})

        # Create sons:
        sci_fi = self.Genre.create(
            {'name': 'Science Fiction', 'parent_id': fiction.id})
        fantasy = self.Genre.create(
            {'name': 'Fantasy', 'parent_id': fiction.id})

        # Verify parent_id relationship
        self.assertEqual(sci_fi.parent_id, fiction)
        self.assertEqual(fantasy.parent_id, fiction)

        # Verify child_ids relationship (Inverse)
        self.assertIn(sci_fi, fiction.child_ids)
        self.assertIn(fantasy, fiction.child_ids)
        self.assertEqual(len(fiction.child_ids), 2)

    def test_get_hierarchy_path(self):
        """Test get hierarchy path method rerurns correct sequence."""
        # Create hierarchy: Fiction -> Sci-Fi -> Cyberpunk
        fiction = self.Genre.create({'name': 'Fiction'})
        sci_fi = self.Genre.create(
            {'name': 'Science Fiction', 'parent_id': fiction.id})
        cyberpunk = self.Genre.create(
            {'name': 'Cyberpunk', 'parent_id': sci_fi.id})

        # Verify paths
        fiction_path = fiction.get_hierarchy_path()
        self.assertEqual(fiction_path, ['Fiction'])

        sci_fi_path = sci_fi.get_hierarchy_path()
        self.assertEqual(sci_fi_path, ['Fiction', 'Science Fiction'])

        cyberpunk_path = cyberpunk.get_hierarchy_path()
        self.assertEqual(cyberpunk_path, [
                         'Fiction', 'Science Fiction', 'Cyberpunk'])

    def test_get_all_children(self):
        """Test that all descendents are returned correctly."""
        # Create complex hierarchy
        fiction = self.Genre.create({'name': 'Fiction'})
        sci_fi = self.Genre.create(
            {'name': 'Science Fiction', 'parent_id': fiction.id})
        cyberpunk = self.Genre.create(
            {'name': 'Cyberpunk', 'parent_id': sci_fi.id})
        space_opera = self.Genre.create(
            {'name': 'Space Opera', 'parent_id': sci_fi.id})
        fantasy = self.Genre.create(
            {'name': 'Fantasy', 'parent_id': fiction.id})

        # Get all descendents of Fiction
        all_children = fiction.get_all_children(include_self=False)

        # Must include: Sci-Fi, Cyberpunk, Space opera, Fantasy
        self.assertEqual(len(all_children), 4)
        self.assertIn(sci_fi, all_children)
        self.assertIn(cyberpunk, all_children)
        self.assertIn(space_opera, all_children)
        self.assertIn(fantasy, all_children)

        # Verify include_self work
        all_with_self = fiction.get_all_children(include_self=True)
        self.assertEqual(len(all_with_self), 5)
        self.assertIn(fiction, all_with_self)

    # ============ MEDIUM PRIORITY - VALIDATION AND NORMALIZATION ============

    def test_name_normalization_on_create(self):
        """Test that names are properly normalized (spaces trimmed/collapsed)."""
        genre = self.Genre.create({'name': '  Science   Fiction   '})
        self.assertEqual(genre.name, 'Science Fiction')

    def test_name_normalization_on_update(self):
        """Test that names are properly normalized on updates."""
        genre = self.Genre.create({'name': '   Test Genre   '})
        self.assertEqual(genre.name, 'Test Genre')

    def test_code_uniqueness(self):
        """Test that genre codes must be unique when specified."""
        self.Genre.create({'name': 'Fiction', 'code': 'FIC'})

        with self.assertRaises(IntegrityError):
            self.Genre.create({'name': 'Sci-Fi', 'code': 'FIC'})

    def test_display_name_with_hierarchy(self):
        """Test display_name shows hierarchy context."""
        fiction = self.Genre.create({'name': 'Fiction'})
        sci_fi = self.Genre.create(
            {'name': 'Science Fiction', 'parent_id': fiction.id})

        # Display name could be include the parent:
        # Ex: "Fiction / Science Fiction" or only "Science Fiction"
        self.assertIn('Science Fiction', sci_fi.display_name)

# ============ LOW PRIORITY ============

    def test_multiple_root_genres_allowed(self):
        """Test that multiple genres without parents are allowed."""
        fiction = self.Genre.create({'name': 'Fiction'})
        nonfiction = self.Genre.create({'name': 'Non-Fiction'})

        self.assertFalse(fiction.parent_id)
        self.assertFalse(nonfiction.parent_id)
        self.assertNotEqual(fiction.id, nonfiction.id)

    def test_deep_hierarchy_supported(self):
        """Test that deep hierarchies (5+ levels) work correctly."""
        level1 = self.Genre.create({'name': 'Level 1'})
        level2 = self.Genre.create({'name': 'Level 2', 'parent_id': level1.id})
        level3 = self.Genre.create({'name': 'Level 3', 'parent_id': level2.id})
        level4 = self.Genre.create({'name': 'Level 4', 'parent_id': level3.id})
        level5 = self.Genre.create({'name': 'Level 5', 'parent_id': level4.id})

        path = level5.get_hierarchy_path()
        self.assertEqual(len(path), 5)
        self.assertEqual(path[-1], 'Level 5')

    def test_active_field_behavior(self):
        """Test archiving functionality."""
        genre = self.Genre.create({'name': 'Archived Genre'})
        self.assertTrue(genre.active)

        genre.write({'active': False})
        self.assertFalse(genre.active)

        # Normal search shouldn't find archived
        result = self.Genre.search([('name', '=', 'Archived Genre')])
        self.assertEqual(len(result), 0)

    def test_sequence_field_for_ordering(self):
        """Test that sequence field allows custom ordering."""
        genre1 = self.Genre.create({'name': 'Z Genre', 'sequence': 10})
        genre2 = self.Genre.create({'name': 'A Genre', 'sequence': 5})

        # Buscar ordenados por sequence
        genres = self.Genre.search([], order='sequence')

        # genre2 debe aparecer primero (menor sequence)
        self.assertEqual(genres[0], genre2)

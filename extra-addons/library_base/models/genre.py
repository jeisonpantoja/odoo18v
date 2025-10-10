# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryGenre(models.Model):
    """
        Represents hierarchical categorization system for books. Supports parent-child relationships to create taxonomies.

        TDD Phase 1: Focus on hierarchy and validation
    """

    _name = 'library.genre'
    _description = 'Library Genre'
    _parent_name = 'parent_id'  # Indicate which is the parent field for hierarchies
    _parent_store = True        # Enable the parent_path automatic system
    _parent_order = 'name'
    _order = 'parent_path, sequence, name'

    # ============ CORE FIELDS ============

    name = fields.Char(
        string='Genre Name',
        required=True,
        index=True,
        help="Name of the genre or category"
    )

    code = fields.Char(
        string='Code',
        index=True,
        help="Short code for the genre (e.g.: 'SCI-FI', 'HIST')"
    )

    description = fields.Text(
        string='Description',
        help="Description of the genre or category"
    )

    color = fields.Integer(
        string='Color',
        help='Color code for UI display'
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of display'
    )

    # ============ HIERARCHY FIELDS ============

    parent_id = fields.Many2one(
        comodel_name='library.genre',
        string='Parent Genre',
        ondelete='cascade',
        index=True,
        help='Parent genre in the hierarchy'
    )

    child_ids = fields.One2many(
        comodel_name='library.genre',
        inverse_name='parent_id',
        string='Child Genres',
        help='Child genres in the hierarchy'
    )

    # This field work automatically with parent_store
    parent_path = fields.Char(
        string='Parent Path',
        index=True,
        help='Materialized path for efficient hierarchy queries'
    )

    # ============ SYSTEM FIELDS ============

    active = fields.Boolean(
        default=True,
        help="Uncheck to archive the genre"
    )

    # ============ COMPUTED FIELDS ============

    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
        help="Formatted name for UI display"
    )

    @api.depends('name', 'parent_id.display_name')
    def _compute_display_name(self):
        """Compute display name based on name and parent when available."""
        for record in self:
            if record.parent_id:
                # Si el padre tiene ya display_name, lo usamos + "/" + propio nombre
                record.display_name = f"{record.parent_id.display_name} / {record.name}"
            else:
                record.display_name = record.name

    # ============ CONSTRAINTS ============

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Genre code must be unique!')
    ]

    @api.constrains('name')
    def _check_name_not_empty(self):
        """Validate that the genre name is not empty."""
        for record in self:
            if not record.name or not record.name.strip():
                raise ValidationError(
                    "Genre name is required and cannot be empty."
                )

    @api.constrains('parent_id')
    def _check_genre_recursion(self):
        """validate that not circular hierarchies exist."""
        if not self._check_recursion():
            raise ValidationError("Error! You cannot create recursive genres.")

    # ============ DATA NORMALIZATION ============

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to normalize name."""
        for vals in vals_list:
            if 'name' in vals:
                vals['name'] = self._normalize_name(vals['name'])
        return super().create(vals_list)

    def write(self, vals):
        """Override write to normalize name on updates."""
        if 'name' in vals:
            vals['name'] = self._normalize_name(vals['name'])
        return super().write(vals)

    def _normalize_name(self, name):
        """Normalize names by stripping extra spaces."""
        if not name:
            return name
        return ' '.join(name.strip().split())

    # ============ HIERARCHY NAVIGATION METHODS ============

    def get_hierarchy_path(self):
        """
        Return list of genre names from root to current.

        Returns:
            list: List of genre names. e.g.:  For Cyberpunk son of Sci-Fi son of Fiction. Return: ['Fiction', 'Science Fiction', 'Cyberpunk']
        """
        self.ensure_one()
        path = []
        current = self
        while current:
            path.insert(0, current.name)
            current = current.parent_id
        return path

    def get_all_children(self, include_self=False):
        """
        Return all descendant genres (children, grandchildren, etc.) of the current genre.

        Args:
            include_self (bool):

        Returns:
            list: List of child genres.
        """
        self.ensure_one()
        domain = [('parent_path', '=like', self.parent_path + '%')]
        if not include_self:
            domain += [('id', '!=', self.id)]
        return self.search(domain)

    # ============ PUBLIC API METHODS ============

    def as_dict(self, fields=None):
        """
        Return genre data as a dictionary for API usage.

        Args:
            fields (list, optional): List of fields to include in the dictionary.

        Returns:
            dict: Dictionary containing genre data. 
        """
        if not fields:
            fields = ['id', 'name', 'code', 'description', 'color', 'sequence']

        result = {}
        for field in fields:
            if hasattr(self, field):
                value = getattr(self, field)
                result[field] = value
        return result

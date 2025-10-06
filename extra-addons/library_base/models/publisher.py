# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryPublisher(models.Model):
    """
    Represents publishing companies or organizations that publish books.

    TDD Phase 1: Basic fields and validations only
    """

    _name = 'library.publisher'
    _description = 'Library Publisher'
    _order = 'name'

    # ============ CORE FIELDS ============

    name = fields.Char(
        string='Publisher name',
        required=True,
        index=True,
        help="Name of the publishing company"
    )

    website = fields.Char(
        string='Website',
        help="Official website of the publisher"
    )

    founded_year = fields.Integer(
        string='Founded Year',
        help="Year the publisher was founded"
    )

    country = fields.Char(
        string='Country',
        help="Country where the publisher is located"
    )

    description = fields.Text(
        string='Description',
        help="Brief description of the publisher"
    )

    # ============ SYSTEM FIELDS ============

    contact_id = fields.Many2one(
        'res.partner',
        string='Contact Information',
        ondelete='set null',
        help="Contact information for the publisher"
    )

    active = fields.Boolean(
        default=True,
        help="Uncheck to archive the publisher"
    )

    # ============ COMPUTED FIELDS ============

    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
        help="Formatted name for UI display"
    )

    @api.depends('name', 'country')
    def _compute_display_name(self):
        """Compute display name based on name and country when available."""
        for record in self:
            display = record.name or 'Unknown Publisher'
            if record.country:
                display += f" ({record.country})"
            record.display_name = display

    # ============ CONSTRAINTS ============

    @api.constrains('name')
    def _check_name_not_empty(self):
        """Validate that the publisher name is not empty."""
        for record in self:
            if not record.name or not record.name.strip():
                raise ValidationError(
                    "Publisher name is required and cannot be empty."
                )

    @api.constrains('founded_year')
    def _check_founded_year_valid(self):
        """Validate that founded year is reasonable (>= 1400 and <= current year)."""
        current_year = fields.Date.today().year
        for record in self:
            if record.founded_year:
                if record.founded_year < 1400:
                    raise ValidationError(
                        "Founded year must be 1400 or later."
                    )
                if record.founded_year > current_year:
                    raise ValidationError(
                        f"Founded year cannot be in the future ({current_year})."
                    )

    @api.constrains('website')
    def _check_website_format(self):
        """Validate that the website URL starts with http:// or https://."""
        for record in self:
            if record.website and not (record.website.startswith('http://') or record.website.startswith('https://')):
                raise ValidationError(
                    "Website URL must start with 'http://' or 'https://'."
                )

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

    # ============ PUBLIC API - BUSINESS METHODS ============

    def as_dict(self, fields=None):
        """
        Return publisher data as a dictionary for API usage.

        Args:
            fields (list, optional): List of fields to include in the dictionary.

        Returns:
            dict: Dictionary containing publisher data.
        """
        if not fields:
            fields = ['id', 'name', 'country', 'website', 'founded_year']

        result = {}
        for field in fields:
            if hasattr(self, field):
                value = getattr(self, field)
                result[field] = value
        return result

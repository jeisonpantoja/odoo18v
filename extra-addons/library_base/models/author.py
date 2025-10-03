# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryAuthor(models.Model):
    """
    Represents a person who writes or contributes to books.
    This model serves as the foundational entity for author attribution in the library system.

    TDD Phase 1: Basic fields and validations only
    - Commented out dependencies on library.book
    - Commented out mail tracking features
    - Focus on core author data and validation tests
    """

    _name = 'library.author'
    _description = 'Library Author'
    _order = 'name'

    # TDD Phase 1: Comment out mail inheritance until we need messaging features
    # _inherit = ['mail.thread', 'mail.activity.mixin']

    # ============ CAMPOS PRINCIPALES ============

    name = fields.Char(
        string='Full Name',
        required=True,
        index=True,
        # tracking=True,  # Commented until mail.thread is added
        help="Full name of the author"
    )

    birth_date = fields.Date(
        string='Date of Birth',
        # tracking=True,  # Commented until mail.thread is added
        help="Date of birth"
    )

    death_date = fields.Date(
        string='Date of Death',
        # tracking=True,  # Commented until mail.thread is added
        help="Date of death"
    )

    country = fields.Char(
        string='Country of Origin',
        help="Country of origin"
    )

    biography = fields.Text(
        string='Biography',
        help="Brief biographical information"
    )

    # ============ CAMPOS DE SISTEMA ============

    partner_id = fields.Many2one(
        'res.partner',
        string='Contact Information',
        ondelete='set null',
        help="Related contact record for additional information"
    )

    active = fields.Boolean(
        default=True,
        help="Uncheck to archive the author"
    )

    # ============ RELACIONES (TDD Phase 2) ============

    # TDD Phase 1: Comment out book relationship until library.book exists
    # book_ids = fields.Many2many(
    #     'library.book',
    #     'library_book_author_rel',
    #     'author_id',
    #     'book_id',
    #     string='Books',
    #     help="Books authored by this person"
    # )

    # ============ CAMPOS COMPUTADOS ============

    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
        help="Formatted name for UI display with dates"
    )

    # TDD Phase 1: Comment out books_count until book_ids exists
    # books_count = fields.Integer(
    #     string='Books Count',
    #     compute='_compute_books_count',
    #     help="Number of books authored"
    # )

    # ============ CAMPOS COMPUTADOS - IMPLEMENTACIÓN ============

    @api.depends('name', 'birth_date', 'death_date')
    def _compute_display_name(self):
        """
        Computa el nombre para mostrar incluyendo fechas cuando están disponibles.

        TDD Phase 1: Testing computed fields with basic dependencies
        """
        for record in self:
            display = record.name or 'Unknown Author'

            # Construir información de fechas si están disponibles
            if record.birth_date or record.death_date:
                dates = []
                if record.birth_date:
                    dates.append(str(record.birth_date.year))
                if record.death_date:
                    dates.append(str(record.death_date.year))
                display += f" ({'-'.join(dates)})"

            record.display_name = display

    # TDD Phase 1: Comment out until book_ids relationship exists
    # @api.depends('book_ids')
    # def _compute_books_count(self):
    #     """Cuenta el número de libros del autor."""
    #     for record in self:
    #         record.books_count = len(record.book_ids)

    # ============ VALIDACIONES Y CONSTRAINTS ============

    @api.constrains('name')
    def _check_name_not_empty(self):
        """
        Valida que el nombre del autor no esté vacío.

        TDD Phase 1: Testing basic field validation
        """
        for record in self:
            if not record.name or not record.name.strip():
                raise ValidationError(
                    "Author name is required and cannot be empty."
                )

    @api.constrains('birth_date')
    def _check_birth_date_not_future(self):
        """
        Valida que la fecha de nacimiento no esté en el futuro.

        TDD Phase 1: Testing date validation logic
        """
        for record in self:
            if record.birth_date and record.birth_date > fields.Date.today():
                raise ValidationError(
                    "Birth date cannot be in the future."
                )

    @api.constrains('birth_date', 'death_date')
    def _check_death_after_birth(self):
        """
        Valida que la fecha de muerte sea posterior al nacimiento.

        TDD Phase 1: Testing cross-field validation
        """
        for record in self:
            if (record.birth_date and record.death_date and
                    record.death_date < record.birth_date):
                raise ValidationError(
                    "Death date must be after birth date."
                )

    # ============ NORMALIZACIÓN DE DATOS ============

    @api.model_create_multi
    def create(self, vals_list):
        """
        Sobrescribe el método create para normalizar datos.

        TDD Phase 1: Testing data normalization on create
        """
        for vals in vals_list:
            if 'name' in vals:
                vals['name'] = self._normalize_name(vals['name'])
        return super().create(vals_list)

    def write(self, vals):
        """
        Sobrescribe el método write para normalizar datos en actualizaciones.

        TDD Phase 1: Testing data normalization on write
        """
        if 'name' in vals:
            vals['name'] = self._normalize_name(vals['name'])
        return super().write(vals)

    def _normalize_name(self, name):
        """
        Normaliza nombres eliminando espacios extra.

        TDD Phase 1: Testing private utility methods
        """
        if not name:
            return name
        # Elimina espacios al inicio/final y colapsa espacios múltiples
        return ' '.join(name.strip().split())

    # ============ API PÚBLICA - MÉTODOS DE NEGOCIO ============

    # TDD Phase 1: Comment out until library.book model exists
    # def get_books(self, domain=None):
    #     """Returns books authored by this person."""
    #     # Implementation will come in Phase 2
    #     pass

    def as_dict(self, fields=None):
        """
        Retorna datos del autor como diccionario para uso en APIs.

        TDD Phase 1: Testing API serialization methods
        """
        if not fields:
            fields = ['id', 'name', 'country', 'birth_date', 'death_date']

        result = {}
        for field in fields:
            if hasattr(self, field):
                value = getattr(self, field)
                # Manejar campos de fecha para serialización JSON
                if hasattr(value, 'isoformat'):  # Es una fecha
                    value = value.isoformat() if value else None
                result[field] = value
        return result

    # ============ MÉTODOS DE BÚSQUEDA ============

    @api.model
    def search_authors(self, domain=None, limit=None):
        """
        Búsqueda optimizada de autores.

        TDD Phase 1: Testing model search methods
        """
        if domain is None:
            domain = []
        return self.search(domain, limit=limit, order='name')

    # TDD Phase 1: Comment out mail.thread methods until inheritance is added
    # def _track_subtype(self, init_values):
    #     """Personaliza los subtipos de seguimiento para mensajería."""
    #     # Implementation will come when mail.thread is added
    #     pass

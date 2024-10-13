from odoo import api, fields, models, tools, _

import logging

_logger = logging.getLogger(__name__)

class BookCategory(models.Model):
    _name = "book_library.book.category"

    name = fields.Char(string="Category Name", size=255)
    description = fields.Text(string="Description")
    books_count = fields.Integer(string="Books count", store=False, compute='_compute_books_count')

    @api.depends("name") # todo: `name` must change
    def _compute_books_count(self):
        for record in self:
            record.books_count = 0

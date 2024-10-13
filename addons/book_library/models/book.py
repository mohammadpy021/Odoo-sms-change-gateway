from odoo import api, fields, models, tools, _

import logging

_logger = logging.getLogger(__name__)

class Book(models.Model):
    _name = "book_library.book"

    name = fields.Char(string="Name", size=255)
    author = fields.Char(string="Author", size=255)
    category = fields.Many2one("book_library.book.category",string="Book Category", ondelete='cascade',)
    isbn = fields.Char(string="Books ISBN", size=255)
    status = fields.Selection(string="Books Status", selection=[('is_borrowed', 'Borrowed'),
                                         ('on_hand', 'In Library'),
                                         ('not_available', 'Not Available')
                                         ], default='on_hand')

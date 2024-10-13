from odoo import api, fields, models, tools, _

import logging

_logger = logging.getLogger(__name__)

class BookBorrowingHistory(models.Model):
    _name = "book_library.book.borrowing.history"

    date_borrowed = fields.Datetime(string="Borrowed Date")
    date_back = fields.Datetime(string="Back Date")
    book_id = fields.Many2one("book_library.book", string="Book", ondelete="cascade")
    library_member_id = fields.Many2one("res.partner", string="Library Member", ondelete="cascade")



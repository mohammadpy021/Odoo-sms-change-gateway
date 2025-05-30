# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import re
import textwrap
from binascii import Error as binascii_error
from collections import defaultdict

from odoo import _, api, Command, fields, models, modules, tools
from odoo.exceptions import AccessError
from odoo.osv import expression
from odoo.tools import clean_context, groupby as tools_groupby, SQL

_logger = logging.getLogger(__name__)


class MessageCustom(models.Model):
    _inherit= 'mail.message'

    provider_id = fields.Many2one(
        string='Provider',
        comodel_name='sms.integration.providers',
        ondelete='set null',
        tracking=True
    )
    short_code_id = fields.Many2one(
        string='پیش شماره',
        comodel_name='sms.integration.short_codes',
        ondelete='set null',
        tracking=True
    )
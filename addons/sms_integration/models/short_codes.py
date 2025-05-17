import logging
from odoo import models, fields


class ShortCode(models.Model): 
    _name = 'sms.integration.short_codes'
    _rec_name = 'short_code'
    
    _loggerer = logging.getLogger(__name__)
    
    provider_id = fields.Many2one(
        comodel_name='sms.integration.providers',
        string='Provider ID',
        required=True
    )
    
    short_code = fields.Char(size=50, string="Short Code",required=True, help="example:30005090504425")

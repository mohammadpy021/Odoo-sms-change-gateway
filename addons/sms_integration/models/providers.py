import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Providers(models.Model):
    _name = 'sms.integration.providers'
    _rec_name = 'provider_name'
    
    _loggerer = logging.getLogger(__name__)
    
    name = fields.Char(string="Name",size=255, help="Name of the provider")
    
    provider_name = fields.Selection(
        required=True,
        string='field_name',
        selection=[('web_one', 'web one'), ('magfa', 'magfa'),('0098', '0098') ]
    )
    
    
    short_code_ids = fields.One2many('sms.integration.short_codes', 'provider_id', string='سر شماره')
    provider_site = fields.Char(string="Provider Site",size=255, help="website of the provider")
    api_url =  fields.Char('API URL', help='example : https://www.odoo.com')
    api_key =  fields.Char('API KEY')
    username = fields.Char('User name')
    password = fields.Char('Password')
    #TODO: sms_id?
    # class_name = fields.Char('Class Name', help="a class name for handling the send and receive defined in tools folder")

    @api.depends('provider_name')
    def _compute_name(self):
        for record in self:
            record.name = record.provider_name
            
    @api.constrains('provider_name')
    def _check_unique_provider_name(self):
        for record in self:
            existing_providers = self.search([('provider_name', '=', record.provider_name), ('id', '!=', record.id)])
            if existing_providers:
                raise ValidationError(f"Provider '{record.provider_name}' already exists. You cannot create duplicate providers.")

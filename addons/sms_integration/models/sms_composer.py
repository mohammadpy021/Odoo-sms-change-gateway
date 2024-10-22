import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)
class SmsComposerCustom(models.TransientModel):
    # _name = 'ModelName'
    # _description = 'ModelName'
    _inherit="sms.composer"
    # _rec_name = 'provider_id'

    provider_id = fields.Many2one(
        string = 'Provider',
        comodel_name='sms.integration.providers',
        ondelete='set null', 
    )
    short_code_id = fields.Many2one(
        string = 'short code',
        comodel_name='sms.integration.short_codes',
        ondelete='set null',
        # domain=[('provider_id','=','provider_id')]
    )
    # mail_message_id = fields.Many2one('mail.message', string='Related Mail Message', required=True, ondelete="cascade")
    
    
    # def _prepare_mass_sms(self, records, sms_record_values):
    #     sms_create_vals = [sms_record_values[record.id] for record in records]
    #     return self.env['sms.sms'].sudo().create(sms_create_vals)

    # provider_id_name = fields.Char(string='Related Name', compute='_compute_provider_id_name', store=True)  

    # @api.depends('provider_id')
    # def _compute_provider_id_name(self):
    #     for record in self:
    #         record.provider_id_name = f"{record.provider_id.name}" if record.provider_id else False
    
    
    
    
    def _action_send_sms_numbers(self):

    
        sms_values = [{'body': self.body, 'number': number, 'provider_id': self.provider_id.id,'short_code_id':self.short_code_id.id } for number in self.sanitized_numbers.split(',')]        
        
        self.env['sms.sms'].sudo().create(sms_values).send()
        return True

    # def _prepare_mass_sms(self, records, sms_record_values):
    #     sms_values = [{'body': self.body, 'number': number, 'provider_id': self.provider_id.id,'short_code_id':self.short_code_id.id } for number in self.sanitized_numbers.split(',')]
        
    #     # sms_create_vals = [sms_record_values[record.id] for record in records]
    #     return self.env['sms.sms'].sudo().create(sms_values)
    
    # def action_send_sms(self):
        # if self.composition_mode in ('numbers', 'comment'):
        #     if self.comment_single_recipient and not self.recipient_single_valid:
        #         raise UserError(_('Invalid recipient number. Please update it.'))
        #     elif not self.comment_single_recipient and self.recipient_invalid_count:
        #         raise UserError(_('%s invalid recipients', self.recipient_invalid_count))
        # self._action_send_sms()
    
    
    
        # sms_values = [{'body': self.body, 'number': number, 'provider_id': self.provider_id.id,'short_code_id':self.short_code_id.id } for number in self.sanitized_numbers.split(',')]
        # self.env['sms.sms'].sudo().create(sms_values).send()
        # return True


    # def _action_send_sms(self):
    # i used this
    #     subtype_id = self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note')
    #     if self.sanitized_numbers:
    #         sms_values = [{'partner_id':self.res_id,'body': self.body, 'number': number, 'provider_id': self.provider_id.id,'short_code_id':self.short_code_id.id } for number in self.sanitized_numbers.split(',')]
    #     else : 
            
    #         records = self._get_records()
            
    #         # model = mail_message_id._message_notification_format()[0]['model'] 
    #         # res_model_name  = mail_message_id._message_notification_format()[0]['res_model_name']
    #         # message_type  = mail_message_id._message_notification_format()[0]['message_type']
            
    #         # companies =  RecordsModel.browse(res_ids)._mail_get_companies(default=self.env.company) #TODO: to browse 
    #         vals = {
    #         # 'subject': 'SMS Notification', 
    #         #-{self.env.company[self.res_id]}-{self.env.company[self.res_id].id}
    #         'body': f"{self.body}",  # text of the message
    #         # 'parent_id' : self.res_id, 
    #         'partner_ids': [(6, 0, [self.res_id])],  # the contact
    #         'author_id': self.env.user.partner_id.id,  # the author of message
    #         # 'provider_id': self.provider_id.id,  
    #         # 'short_code_id': self.short_code_id.id,   
    #         'model':  self.res_model,   # 'model': 'res.partner'
           
    #         # 'model': model,  
    #         # 'res_id': self.id,  
    #         'res_id': self.res_id,  
    #         'subtype_id' :subtype_id,
    #         'message_type': 'sms',
            
    #         'record_company_id':   self.env.company.id,
    #         # 'record_company_id':records.company_id, #returned null
    #         # 'record_company_id': companies[res_id].id,
            
    #     }
    #         mail_message = self.env['mail.message'].create(vals)
    #         mail_message_id = mail_message.id
           

            
            
    #         # self : message
    #         # records = user : self.res_id = records.id
    #         # sms_values = [{'body': f"{self.read()}{records.id}{self.id}{self.res_id}{self.res_model}{self.sanitized_numbers}{self.template_id}", 'number': self.numbers, 'provider_id': self.provider_id.id,'short_code_id':self.short_code_id.id }]
    #         sms_values = [{'mail_message_id':mail_message_id,'partner_id':self.res_id, 'body': self.body, 'number': self.recipient_single_number, 'provider_id': self.provider_id.id,'short_code_id':self.short_code_id.id }]
    #     # mail_message_id = self.env['sms.sms'].sudo().create('mail.message')
    #     self.env['sms.sms'].sudo().create(sms_values).send()
    #     return True
    
    # def _action_send_sms(self):
    #     records = self._get_records()
    #     if self.composition_mode == 'numbers':
    #         return self._action_send_sms_numbers()
    #     elif self.composition_mode == 'comment':
    #         if records is None or not isinstance(records, self.pool['mail.thread']):
    #             return self._action_send_sms_numbers()
    #         # the two lines of below will run
    #         if self.comment_single_recipient:
    #             return self._action_send_sms_comment_single(records)
    #         else:
    #             return self._action_send_sms_comment(records)
    #     # else:
    #     #     return self._action_send_sms_mass(records)


    # def _action_send_sms_comment(self, records=None):
    
    #     records = records if records is not None else self._get_records()
    #     subtype_id = self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note')

    #     messages = self.env['mail.message']
    #     all_bodies = self._prepare_body_values(records)
        
    #     for record in records:
    #         messages += record._message_sms(
    #             all_bodies[record.id],
    #             subtype_id=subtype_id,
    #             number_field=self.number_field_name,
    #             sms_numbers=self.sanitized_numbers.split(',') if self.sanitized_numbers else None,
    #             )
            
    # #     values = {
    # #     'res_id': record.id,  
    # #     'model': record._name  
    # # }
    #     # message_id = messages._get_message_id(values)   
    #     # message_id = messages.message_id   
    #     # sms_values = {'provider_id': self.provider_id.id,'short_code_id':self.short_code_id.id }
    #     # sms_record = self.env['sms.sms'].sudo().search([('mail_message_id', '=', message_id)])
    #     # # if sms_record:
    #     # sms_record.write(sms_values).send() #TODO:
            
    #     # sms_records = self.env['sms.sms'].sudo().search([('res_id', '=', record.id)], limit=1)  # بسته به نیاز خود، فیلتر را اصلاح کنید
    #     # self.env['sms.sms'].sudo().wri(sms_values).send()
    #     return messages
    
    
    
    
    def _action_send_sms_comment(self, records=None):
        # messages = self.env['mail.message']
        records = records if records is not None else self._get_records()
        # records = self._get_records()
        
        subtype_id = self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note')
        if self.sanitized_numbers:
            sms_values = [{'partner_id':self.res_id,'body': self.body, 'number': number, 'provider_id': self.provider_id.id,'short_code_id':self.short_code_id.id } for number in self.sanitized_numbers.split(',')]
        else : 
            # model = mail_message_id._message_notification_format()[0]['model'] 
            # res_model_name  = mail_message_id._message_notification_format()[0]['res_model_name']
            # message_type  = mail_message_id._message_notification_format()[0]['message_type']
            
            # companies =  RecordsModel.browse(res_ids)._mail_get_companies(default=self.env.company) #TODO: to browse 
            vals = {
            # 'subject': 'SMS Notification', 
            #-{self.env.company[self.res_id]}-{self.env.company[self.res_id].id}
            'body': f"{self.body}",  # text of the message
            # 'parent_id' : self.res_id, 
            'partner_ids': [(6, 0, [self.res_id])],  # the contact
            'author_id': self.env.user.partner_id.id,  # the author of message
            # 'provider_id': self.provider_id.id,  
            # 'short_code_id': self.short_code_id.id,   
            'model':  self.res_model,   # 'model': 'res.partner'
            
            # 'model': model,  
            # 'res_id': self.id,  
            'res_id': self.res_id,  
            'subtype_id' :subtype_id,
            'message_type': 'sms',
            
            'record_company_id':   self.env.company.id,
            # 'record_company_id':records.company_id, #returned null
            # 'record_company_id': companies[res_id].id,
        }
            mail_message = self.env['mail.message'].create(vals)
            mail_message_id = mail_message.id
            

            
            
            # self : message
            # records = user : self.res_id = records.id
            # sms_values = [{'body': f"{self.read()}{records.id}{self.id}{self.res_id}{self.res_model}{self.sanitized_numbers}{self.template_id}", 'number': self.numbers, 'provider_id': self.provider_id.id,'short_code_id':self.short_code_id.id }]
            sms_values = [{'mail_message_id':mail_message_id,'partner_id':self.res_id, 'body': self.body, 'number': self.recipient_single_number, 'provider_id': self.provider_id.id,'short_code_id':self.short_code_id.id }]
        # mail_message_id = self.env['sms.sms'].sudo().create('mail.message')

        return self.env['sms.sms'].sudo().create(sms_values).send()
    
    # def _action_send_sms_mass(self, records=None):
    #     records = records if records is not None else self._get_records()

    #     sms_record_values = self._prepare_mass_sms_values(records)
    #     sms_all = self._prepare_mass_sms(records, sms_record_values)
    #     if sms_all and self.mass_keep_log and records and isinstance(records, self.pool['mail.thread']):
    #         log_values = self._prepare_mass_log_values(records, sms_record_values)
    #         records._message_log_batch(**log_values)

    #     if sms_all and self.mass_force_send:
    #         sms_all.filtered(lambda sms: sms.state == 'outgoing').send(auto_commit=False, raise_exception=False)
    #         return self.env['sms.sms'].sudo().search([('id', 'in', sms_all.ids)])
    #     return sms_all
   
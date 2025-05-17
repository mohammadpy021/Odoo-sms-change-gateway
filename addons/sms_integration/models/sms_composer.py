import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)
class SmsComposerCustom(models.TransientModel):
    _inherit="sms.composer"

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
        
    def _action_send_sms_numbers(self):
        sms_values = [{'body': self.body, 'number': number, 'provider_id': self.provider_id.id,'short_code_id':self.short_code_id.id } for number in self.sanitized_numbers.split(',')]        

        self.env['sms.sms'].sudo().create(sms_values).send()
        return True



    def _action_send_sms_comment(self, records=None):
        records = records if records is not None else self._get_records()
        subtype_id = self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note')

        messages = self.env['mail.message']
        all_bodies = self._prepare_body_values(records)

        # _logger.info(f'='*40 + f'=records:', records)
        # _logger.info(f'='*40 + f'=provider_id:', self.provider_id)

        for record in records:
            messages += record._message_sms(
                all_bodies[record.id],
                subtype_id=subtype_id,
                number_field=self.number_field_name,
                sms_numbers=self.sanitized_numbers.split(',') if self.sanitized_numbers else None,

                #custom
                provider_id=self.provider_id,
                short_code_id=self.short_code_id
            )
        return messages



# the information of Provider and Short_code have to send from here to  sms_sms.py
#     def _action_send_sms_comment(self, records=None):
#         # messages = self.env['mail.message']
    #     records = records if records is not None else self._get_records()
    #     # records = self._get_records()
    #
    #     subtype_id = self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note')
    #     if self.sanitized_numbers:
    #         sms_values = [{'partner_id':self.res_id,'body': self.body, 'number': number, 'provider_id': self.provider_id.id,'short_code_id':self.short_code_id.id } for number in self.sanitized_numbers.split(',')]
    #     else :
    #         # model = mail_message_id._message_notification_format()[0]['model']
    #         # res_model_name  = mail_message_id._message_notification_format()[0]['res_model_name']
    #         # message_type  = mail_message_id._message_notification_format()[0]['message_type']
    #
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
    #
    #         # 'model': model,
    #         # 'res_id': self.id,
    #         'res_id': self.res_id,
    #         'subtype_id' :subtype_id,
    #         'message_type': 'sms',
    #
    #         'record_company_id':   self.env.company.id,
    #         # 'record_company_id':records.company_id, #returned null
    #         # 'record_company_id': companies[res_id].id,
    #     }
    #         mail_message = self.env['mail.message'].create(vals)
    #         mail_message_id = mail_message.id
    #
    #
    #
    #
    #         # self : message
    #         # records = user : self.res_id = records.id
    #         # sms_values = [{'body': f"{self.read()}{records.id}{self.id}{self.res_id}{self.res_model}{self.sanitized_numbers}{self.template_id}", 'number': self.numbers, 'provider_id': self.provider_id.id,'short_code_id':self.short_code_id.id }]
    #         sms_values = [{'mail_message_id':mail_message_id,'partner_id':self.res_id, 'body': self.body,
    #                        'number': self.recipient_single_number,
    #                        'provider_id': self.provider_id.id,
    #                        'short_code_id':self.short_code_id.id }]
    #     # mail_message_id = self.env['sms.sms'].sudo().create('mail.message')
    #
    #     return self.env['sms.sms'].sudo().create(sms_values).send()
    #
    #

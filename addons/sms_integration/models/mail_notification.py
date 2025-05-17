from odoo import api, fields, models


class MailNotification(models.Model):
    _inherit = 'mail.notification'


    IAP_TO_SMS_FAILURE_TYPE = {
        'insufficient_credit': 'sms_credit',  # 8
        'wrong_number_format': 'sms_number_format',  # 16
        'wrong_message_format': 'sms_message_format',  # 16
        'country_not_supported': 'sms_country_not_supported',
        'server_error': 'sms_server',
        'unregistered': 'sms_acc',
        # custom
        'wrong_sender_number': 'sms_sender_number',  # 3
        'wrong_credintail': 'sms_credintail',  # 1
        'limit_per_day': 'sms_per_day',  # 4
        'disabled_webservice': 'sms_webservice',  # 10
        'wrong_recid_code': 'sms_recid_code',  #
    }

    failure_type = fields.Selection(
        selection_add=[
            ('sms_sender_number', 'sender number is wrong'),
            ('sms_credintail', 'username password or api_key is wrong'),
            ('sms_per_day', 'you reached the limitation of sending sms per day'),
            ('sms_webservice', 'webservice is unavailable'),
            ('sms_recid_code', 'no message exists with this code'),
            ('sms_message_format', 'the sms format was announced wrong by Provider')
        ],
        copy=False
    )
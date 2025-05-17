import logging
import threading
from uuid import uuid4
import requests
from werkzeug.urls import url_join
from zeep import Client
import base64
from zeep.exceptions import Fault
import requests
import re 

from odoo import api, fields, models, tools, _
from odoo.addons.sms.tools.sms_api import SmsApi
# from ..tools import SmsApiCusotm
_logger = logging.getLogger(__name__)



class SmsSmsCustom(models.Model):
    _inherit = ['sms.sms']
    # _rec_name = 'provider'

    provider_id = fields.Many2one(
        string = 'Provider',
        comodel_name='sms.integration.providers',
        ondelete='set null'
    )
    short_code_id = fields.Many2one(
        string = 'short code',
        comodel_name='sms.integration.short_codes',
        ondelete='set null'
        # domain=[('provider_id','=','provider_id')]
    )
    

    
    
    IAP_TO_SMS_FAILURE_TYPE = {
        'insufficient_credit': 'sms_credit', #8
        'wrong_number_format': 'sms_number_format', #16
        'wrong_message_format': 'sms_message_format', #16
        'country_not_supported': 'sms_country_not_supported',
        'server_error': 'sms_server',
        'unregistered': 'sms_acc',
        #custom
        'wrong_sender_number': 'sms_sender_number',#3
        'wrong_credintail': 'sms_credintail',#1
        'limit_per_day': 'sms_per_day', #4
        'disabled_webservice':'sms_webservice', #10
        'wrong_recid_code':'sms_recid_code', # 
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

    def _0098(self, messages):

        provider_class = messages[0]['numbers'][0]['provider_class']
        url = provider_class.api_url
       
        parameters = {
            'FROM': provider_class.short_code_ids.short_code,
            'TO': messages[0]['numbers'][0]['number'],
            'TEXT': messages[0]['content'],
            'USERNAME': provider_class.username,
            'PASSWORD': provider_class.password,
            'DOMAIN': 'DOMAIN'
        }


        response = requests.get(url, params=parameters)
        if response.status_code == 200:
           
            match = re.search(r'\d+', response.text)
            response_number = int(match.group())
            _logger.error(f"response_number", response_number)
            if response_number == 0:
                response_state =  "delivered"
            elif response_number == 1 or  response_number ==  2:
                response_state =  "wrong_number_format"
            elif response_number == 3 :
                response_state =  "wrong_sender_number"
            elif response_number in [4, 13] :
                response_state =  "wrong_message_format"
            elif response_number in [5, 6, 12]:
                response_state =  "wrong_credintail"
            elif response_number == 9 :
                response_state =  "insufficient_credit"
            else:
                response_state =  'server_error'
        else:
           response_state =  "servoer_error"

        results = [
              {
                  'uuid': messages[0]['numbers'][0]['uuid'],
                  'state':response_state,
              },
        ]
        _logger.error(f"results of 998", results)
        return results
   
    def _send(self, unlink_failed=False, unlink_sent=True, raise_exception=False):
        """Send SMS after checking the number (presence and formatting)."""
        messages = [{
            'content': body,
            'numbers': [{'number': sms.number, 'uuid': sms.uuid,
                         'provider_class': sms.provider_id,
                        #  'provider_related_name' : sms.provider_name,
                         'provider_id': sms.provider_id.id,
                         'provider_name': sms.provider_id.provider_name,
                        #  'provider_id_name': sms.provider_id_name,
                         'short_code_id': sms.short_code_id.short_code} for sms in body_sms_records],
        } for body, body_sms_records in self.grouped('body').items()]
        # for i in messages:
        _logger.info(f'>>>provider name:', messages[0]['numbers'][0]['provider_class'].provider_name) 
        _logger.info(f'>>>message:', messages)
        
        # delivery_reports_url = url_join(self[0].get_base_url(), '/sms/status')
        provider_class = messages[0]['numbers'][0]['provider_class']
        provider_name = provider_class.provider_name

        try:
            if provider_class.provider_name ==  "0098":
                results = self._0098(messages=messages)
            else:
                raise "provider is not valid"
                _logger.info('provider name is not valid', provider_name)
                
            # response_state = 'delivered' #'wrong_sender_number' #'processing' #'server_error' #success
            
            _logger.info('results :',results)

            # results = SmsApi(self.env)._send_sms_batch(messages, delivery_reports_url=delivery_reports_url)
        except Fault as e:
            _logger.info('Caught exception:', e)
        except Exception as e:
            _logger.info('Sent batch %s SMS: %s: failed with exception %s', len(self.ids), self.ids, e)
            if raise_exception:
                raise
            results = [{'uuid': sms.uuid, 'state': 'server_error'} for sms in self]
        else:
            _logger.info('Send batch %s SMS: %s: gave %s', len(self.ids), self.ids, results)


        results_uuids = [result['uuid'] for result in results]
        all_sms_sudo = self.env['sms.sms'].sudo().search([('uuid', 'in', results_uuids)]).with_context(sms_skip_msg_notification=True)

        for iap_state, results_group in tools.groupby(results, key=lambda result: result['state']):
            sms_sudo = all_sms_sudo.filtered(lambda s: s.uuid in {result['uuid'] for result in results_group})
            if success_state := self.IAP_TO_SMS_STATE_SUCCESS.get(iap_state):
                _logger.info('here is if success_state := self.IAP_TO_SMS_STATE_SUCCESS.get(iap_state): ',success_state)
                
                sms_sudo.sms_tracker_id._action_update_from_sms_state(success_state)
                to_delete = {'to_delete': True} if unlink_sent else {}
                sms_sudo.write({'state': success_state, 'failure_type': False, **to_delete})
            else:
                
                failure_type = self.IAP_TO_SMS_FAILURE_TYPE.get(iap_state, 'unknown')
                # failure_type = 'unknown'
                _logger.info('here is else: ',failure_type)
                if failure_type != 'unknown':
                    sms_sudo.sms_tracker_id._action_update_from_sms_state('error', failure_type=failure_type)
                else:
                    sms_sudo.sms_tracker_id._action_update_from_provider_error(iap_state)
                to_delete = {'to_delete': True} if unlink_failed else {}
                sms_sudo.write({'state': 'error', 'failure_type': failure_type, **to_delete})
        
        
        _logger.info('all_sms_sudo.mail_message_id:',all_sms_sudo.mail_message_id)
        all_sms_sudo.mail_message_id._notify_message_notification_update()
        
        
        
   
    # def _update_sms_state_and_trackers(self, new_state, failure_type=None):
    #     """Update sms state update and related tracking records (notifications, traces)."""
    #     self.write({'state': new_state, 'failure_type': failure_type})
    #     self.sms_tracker_id._action_update_from_sms_state(new_state, failure_type=failure_type)


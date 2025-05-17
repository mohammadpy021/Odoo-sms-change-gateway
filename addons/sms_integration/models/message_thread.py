import logging

from odoo import api, Command, models, fields
from odoo.addons.sms.tools.sms_tools import sms_content_to_rendered_html

import logging
from markupsafe import Markup, escape

from odoo import _, api, exceptions, fields, models, tools, registry, SUPERUSER_ID, Command
from odoo.tools import is_html_empty, html_escape, html2plaintext, parse_contact_from_email


_logger = logging.getLogger(__name__)



class MailThreadCustom(models.AbstractModel):
    _inherit = 'mail.thread'

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


    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, *,
                     body='', subject=None, message_type='notification',
                     email_from=None, author_id=None, parent_id=False,
                     subtype_xmlid=None, subtype_id=False, partner_ids=None,
                     attachments=None, attachment_ids=None, body_is_html=False,
                     **kwargs):

        self.ensure_one()  # should always be posted on a record, use message_notify if no record

        # preliminary value safety check
        self._raise_for_invalid_parameters(
            set(kwargs.keys()),
            forbidden_names={'model', 'res_id', 'subtype'}
        )
        if self._name == 'mail.thread' or not self.id:
            raise ValueError(_("Posting a message should be done on a business document. Use message_notify to send a notification to an user."))
        if message_type == 'user_notification':
            raise ValueError(_("Use message_notify to send a notification to an user."))
        if attachments:
            # attachments should be a list (or tuples) of 3-elements list (or tuple)
            format_error = not tools.is_list_of(attachments, list) and not tools.is_list_of(attachments, tuple)
            if not format_error:
                format_error = not all(len(attachment) in {2, 3} for attachment in attachments)
            if format_error:
                raise ValueError(
                    _('Posting a message should receive attachments as a list of list or tuples (received %(aids)s)',
                      aids=repr(attachment_ids),
                     )
                )
        if attachment_ids and not tools.is_list_of(attachment_ids, int):
            raise ValueError(
                _('Posting a message should receive attachments records as a list of IDs (received %(aids)s)',
                  aids=repr(attachment_ids),
                 )
            )
        attachment_ids = list(attachment_ids or [])
        if partner_ids and not tools.is_list_of(partner_ids, int):
            raise ValueError(
                _('Posting a message should receive partners as a list of IDs (received %(pids)s)',
                  pids=repr(partner_ids),
                 )
            )
        partner_ids = list(partner_ids or [])

        # split message additional values from notify additional values
        msg_kwargs = {key: val for key, val in kwargs.items()
                      if key in self.env['mail.message']._fields}
        notif_kwargs = {key: val for key, val in kwargs.items()
                        if key not in msg_kwargs}

        # Add lang to context immediately since it will be useful in various flows later
        self = self._fallback_lang()

        # Find the message's author
        guest = self.env['mail.guest']._get_guest_from_context()
        if self.env.user._is_public() and guest:
            author_guest_id = guest.id
            author_id, email_from = False, False
        else:
            author_guest_id = False
            author_id, email_from = self._message_compute_author(author_id, email_from, raise_on_email=True)

        if subtype_xmlid:
            subtype_id = self.env['ir.model.data']._xmlid_to_res_id(subtype_xmlid)
        if not subtype_id:
            subtype_id = self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note')

        # automatically subscribe recipients if asked to
        if self._context.get('mail_post_autofollow') and partner_ids:
            self.message_subscribe(partner_ids=list(partner_ids))

        msg_values = dict(msg_kwargs)
        if 'email_add_signature' not in msg_values:
            msg_values['email_add_signature'] = True
        if not msg_values.get('record_name'):
            # use sudo as record access is not always granted (notably when replying
            # a notification) -> final check is done at message creation level
            msg_values['record_name'] = self.sudo().display_name
        if body_is_html and self.user_has_groups("base.group_user"):
            _logger.warning("Posting HTML message using body_is_html=True, use a Markup object instead (user: %s)",
                self.env.user.id)
            body = Markup(body)
        msg_values.update({
            # author
            'author_id': author_id,
            'author_guest_id': author_guest_id,
            'email_from': email_from,
            # document
            'model': self._name,
            'res_id': self.id,
            # content
            'body': escape(body),  # escape if text, keep if markup
            'message_type': message_type,
            'parent_id': self._message_compute_parent_id(parent_id),
            'subject': subject or False,
            'subtype_id': subtype_id,
            # recipients
            'partner_ids': partner_ids,
        })
        # add default-like values afterwards, to avoid useless queries
        if 'record_alias_domain_id' not in msg_values:
            msg_values['record_alias_domain_id'] = self.sudo()._mail_get_alias_domains(default_company=self.env.company)[self.id].id
        if 'record_company_id' not in msg_values:
            msg_values['record_company_id'] = self._mail_get_companies(default=self.env.company)[self.id].id
        if 'reply_to' not in msg_values:
            msg_values['reply_to'] = self._notify_get_reply_to(default=email_from)[self.id]

        msg_values.update(
            self._process_attachments_for_post(attachments, attachment_ids, msg_values)
        )  # attachement_ids, body

        # Custom
        provider_id = msg_values.pop("provider_id")
        short_code_id = msg_values.pop("short_code_id")

        new_message = self._message_create([msg_values])

        # subscribe author(s) so that they receive answers; do it only when it is
        # a manual post by the author (aka not a system notification, not a message
        # posted 'in behalf of', and if still active).
        author_subscribe = (not self._context.get('mail_create_nosubscribe') and
                             msg_values['message_type'] != 'notification')
        if author_subscribe:
            real_author_id = False
            # if current user is active, they are the one doing the action and should
            # be notified of answers. If they are inactive they are posting on behalf
            # of someone else (a custom, mailgateway, ...) and the real author is the
            # message author
            if self.env.user.active:
                real_author_id = self.env.user.partner_id.id
            elif msg_values['author_id']:
                author = self.env['res.partner'].browse(msg_values['author_id'])
                if author.active:
                    real_author_id = author.id
            if real_author_id:
                self._message_subscribe(partner_ids=[real_author_id])

        self._message_post_after_hook(new_message, msg_values)

        msg_values.update({ #Custom
            "provider_id":provider_id.id,
            "short_code_id":short_code_id.id,
        })

        self._notify_thread(new_message, msg_values, **notif_kwargs)
        return new_message






    def _notify_thread_by_sms(self, message, recipients_data, msg_vals=False,
                              sms_content=None, sms_numbers=None, sms_pid_to_number=None,
                              resend_existing=False, put_in_queue=False, **kwargs):
        """ Notification method: by SMS.

        :param message: ``mail.message`` record to notify;
        :param recipients_data: list of recipients information (based on res.partner
          records), formatted like
            [{'active': partner.active;
              'id': id of the res.partner being recipient to notify;
              'groups': res.group IDs if linked to a user;
              'notif': 'inbox', 'email', 'sms' (SMS App);
              'share': partner.partner_share;
              'type': 'customer', 'portal', 'user;'
             }, {...}].
          See ``MailThread._notify_get_recipients``;
        :param msg_vals: dictionary of values used to create the message. If given it
          may be used to access values related to ``message`` without accessing it
          directly. It lessens query count in some optimized use cases by avoiding
          access message content in db;

        :param sms_content: plaintext version of body, mainly to avoid
          conversion glitches by splitting html and plain text content formatting
          (e.g.: links, styling.).
          If not given, `msg_vals`'s `body` is used and converted from html to plaintext;
        :param sms_numbers: additional numbers to notify in addition to partners
          and classic recipients;
        :param pid_to_number: force a number to notify for a given partner ID
          instead of taking its mobile / phone number;
        :param resend_existing: check for existing notifications to update based on
          mailed recipient, otherwise create new notifications;
        :param put_in_queue: use cron to send queued SMS instead of sending them
          directly;
        """
        sms_pid_to_number = sms_pid_to_number if sms_pid_to_number is not None else {}
        sms_numbers = sms_numbers if sms_numbers is not None else []
        sms_create_vals = []
        sms_all = self.env['sms.sms'].sudo()

        # pre-compute SMS data
        body = sms_content or html2plaintext(msg_vals['body'] if msg_vals and 'body' in msg_vals else message.body)
        sms_base_vals = {
            'body': body,
            'mail_message_id': message.id,
            'state': 'outgoing',
        }
        #Custom
        _logger.info(f'=' * 40 + f'=msg_vals.get(provider_id)',  msg_vals.get('provider_id'))
        sms_base_vals.update({'provider_id': msg_vals.get('provider_id'),
                             'short_code_id':msg_vals.get('short_code_id')
                              })

        # notify from computed recipients_data (followers, specific recipients)
        partners_data = [r for r in recipients_data if r['notif'] == 'sms']
        partner_ids = [r['id'] for r in partners_data]
        if partner_ids:
            for partner in self.env['res.partner'].sudo().browse(partner_ids):
                number = sms_pid_to_number.get(partner.id) or partner.mobile or partner.phone
                sms_create_vals.append(dict(
                    sms_base_vals,
                    partner_id=partner.id,
                    number=partner._phone_format(number=number) or number,
                ))
        # notify from additional numbers
        if sms_numbers:
            tocreate_numbers = [
                self._phone_format(number=sms_number) or sms_number
                for sms_number in sms_numbers
            ]
            existing_partners_numbers = {vals_dict['number'] for vals_dict in sms_create_vals}
            sms_create_vals += [dict(
                sms_base_vals,
                partner_id=False,
                number=n,
                state='outgoing' if n else 'error',
                failure_type='' if n else 'sms_number_missing',
            ) for n in tocreate_numbers if n not in existing_partners_numbers]

        # create sms and notification
        existing_pids, existing_numbers = [], []

        #custom
        _logger.info(f'=' * 40 + f'=_notify_thread : sms_create_vals', sms_create_vals)

        if sms_create_vals:
            sms_all |= self.env['sms.sms'].sudo().create(sms_create_vals)

            if resend_existing:
                existing = self.env['mail.notification'].sudo().search([
                    '|', ('res_partner_id', 'in', partner_ids),
                    '&', ('res_partner_id', '=', False), ('sms_number', 'in', sms_numbers),
                    ('notification_type', '=', 'sms'),
                    ('mail_message_id', '=', message.id)
                ])
                for n in existing:
                    if n.res_partner_id.id in partner_ids and n.mail_message_id == message:
                        existing_pids.append(n.res_partner_id.id)
                    if not n.res_partner_id and n.sms_number in sms_numbers and n.mail_message_id == message:
                        existing_numbers.append(n.sms_number)


            notif_create_values = [{
                'author_id': message.author_id.id,
                'mail_message_id': message.id,
                'res_partner_id': sms.partner_id.id,
                'sms_number': sms.number,
                'notification_type': 'sms',
                'sms_id_int': sms.id,
                'sms_tracker_ids': [Command.create({'sms_uuid': sms.uuid})] if sms.state == 'outgoing' else False,
                'is_read': True,  # discard Inbox notification
                'notification_status': 'ready' if sms.state == 'outgoing' else 'exception',
                'failure_type': '' if sms.state == 'outgoing' else sms.failure_type,
                 # 'failure_type': '' if sms.state == 'outgoing' else (#custom
                 #        sms.failure_type if sms.failure_type in
                 #        [key for key, _ in self.env['mail.notification'].fields_get(allfields=['failure_type'])['failure_type']['selection']]
                 #        else 'unknown'
                 #    ),

            } for sms in sms_all if (sms.partner_id and sms.partner_id.id not in existing_pids) or (not sms.partner_id and sms.number not in existing_numbers)]
            if notif_create_values:
                self.env['mail.notification'].sudo().create(notif_create_values)

            if existing_pids or existing_numbers:
                for sms in sms_all:
                    notif = next((n for n in existing if
                                 (n.res_partner_id.id in existing_pids and n.res_partner_id.id == sms.partner_id.id) or
                                 (not n.res_partner_id and n.sms_number in existing_numbers and n.sms_number == sms.number)), False)
                    if notif:
                        notif.write({
                            'notification_type': 'sms',
                            'notification_status': 'ready',
                            'sms_id_int': sms.id,
                            'sms_tracker_ids': [Command.create({'sms_uuid': sms.uuid})],
                            'sms_number': sms.number,
                        })

        if sms_all and not put_in_queue:
            sms_all.filtered(lambda sms: sms.state == 'outgoing').send(auto_commit=False, raise_exception=False)

        return True
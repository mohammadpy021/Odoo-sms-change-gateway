# # -*- coding: utf-8 -*-
# # Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _
from odoo.addons.iap.tools import iap_tools
from odoo.addons.sms.models.sms_sms import SmsApi, SmsSms
from abc import ABC, abstractmethod

class SmsApiAbstract(ABC):
    
    @abstractmethod
    def __init__(self):
        pass
        
    @abstractmethod
    def send(self):
        pass
    

    
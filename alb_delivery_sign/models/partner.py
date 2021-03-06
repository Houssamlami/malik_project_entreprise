# -*- coding: utf-8 -*-

from odoo import models, fields, api
import random
import string

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def get_random_pin(self,stringLength=6):
        lettersAndDigits = string.ascii_letters + string.digits
        return ''.join((random.choice(lettersAndDigits).lower() for i in range(stringLength)))

    pin = fields.Char(string="PIN Client", default=get_random_pin)
    pin_livreur = fields.Char(string="PIN Livreur", default=get_random_pin)

    _sql_constraints = [
        ('pin_client_unique', 'unique(pin)', 'Le pin du client doit être unique'),
        ('pin_livreur_unique', 'unique(pin_livreur)', 'Le pin du livreur doit être unique'),
    ]



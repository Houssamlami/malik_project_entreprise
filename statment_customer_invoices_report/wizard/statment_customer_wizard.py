# -*-coding:Latin-1 -*

from odoo import models, fields, api, _
from datetime import datetime
import time


class StatmentCustomerWizard(models.TransientModel):
    _name = 'statment.customer.wizard'
    
    
    client_id = fields.Many2one('res.partner',string=u"Client", domain="[('customer','=',True)]")
    periode_from =  fields.Date('Start Date', required=True, default= lambda *a: time.strftime('%Y-01-01'))
    periode_to =  fields.Date('End Date', required=True, default= lambda *a: time.strftime('%Y-%m-%d'))
    invoices_id =  fields.Many2many('account.invoice',string=u"Invoices")
    
    
    #get invoice in period
    def _get_invoice_in_period(self):
        #
        if self.client_id and self.periode_from and self.periode_to:       
            invoice = self.env['account.invoice'].search([('partner_id', '=', self.client_id.id),('type', 'in', ['out_invoice','out_refund']),('state', 'in', ['open','paid']),
                                                          ('date_invoice', '>=', self.periode_from),('date_invoice', '<=', self.periode_to),('user_id.name','!=','FATIMAZAHRA Comptabilité')])
            return invoice
    
    #print statement customer 
    @api.multi
    def print_statment_customer_report(self):
        self.invoices_id = self._get_invoice_in_period()
        return self.env.ref('statment_customer_invoices_report.releve_client_report_id').report_action(self)
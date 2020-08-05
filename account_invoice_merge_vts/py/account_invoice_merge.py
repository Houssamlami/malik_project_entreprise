from odoo import models,fields,api,_
from odoo.exceptions import UserError

class account_invoice_merge(models.TransientModel):
    _name = 'account.invoice.merge'
    
    merge = fields.Boolean(string='Merge',default=False)
    date_invoice = fields.Date(string='Invoice Date')
        
    @api.multi
    def merge_account_invoice(self):
        context = dict(self._context or {})
        invoice_ids = self.env['account.invoice'].browse(context.get('active_ids'))
        if len(invoice_ids) <= 1:
            raise UserError(_('Please select multiple Invoice to merge in the list view.... '))
        for invoice_id in invoice_ids:
            if invoice_id.state not in 'draft':
                raise UserError(_('Invoice Must be in Draft State..'))
        for invoice_id in invoice_ids:
            if invoice_ids[0].partner_id.id == invoice_id.partner_id.id:
                merge = True
            if invoice_ids[0].type == invoice_id.type:
                merge = True
            if invoice_ids[0].company_id.id == invoice_id.company_id.id:
                merge = True
            if invoice_ids[0].journal_id.id == invoice_id.journal_id.id:
                merge = True
            if invoice_ids[0].user_id.id == invoice_id.user_id.id:
                merge = True
            else:
                merge = False
                break
        
        if merge:
            partner_id = invoice_ids[0].partner_id.id
            invoice_obj = self.env['account.invoice']
            vals= {
                'partner_id':partner_id,
                'date_invoice':self.date_invoice,
                'type':invoice_ids[0].type
            }
            ac = invoice_obj.create(vals)
            # call the  onchange 
            ac._onchange_partner_id()
            ac._onchange_journal_id()
            ac._onchange_payment_term_date_invoice()
            
            for invoice_id in invoice_ids:
                for invoice_line in invoice_id.invoice_line_ids:
                    invoice_line.copy({'invoice_id':ac.id})
                    invoice_line._compute_price()
                invoice_id.write({'state':'cancel'})
            ac.compute_taxes()
        else:
            raise UserError(_('Can not Merge Invoice! \n Partner,Company,Salesperson and Journal Should be Same'))
                
        return True        
            
            
            

# Author: Damien Crier, Andrea Stirpe, Kevin Graveman, Dennis Sluijk
# Author: Julien Coux
# Copyright 2016 Camptocamp SA, Onestein B.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, exceptions, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools import pycompat
from odoo.exceptions import except_orm, Warning, RedirectWarning


class AgedPartnerBalanceWizard(models.TransientModel):
    """Aged partner balance report wizard."""

    _name = 'aged.partner.balance.wizard'
    _description = 'Aged Partner Balance Wizard'
    
    @api.model
    def _default_account_get(self):
        return self.env['account.account'].search([('name', '=', 'Clients - Ventes de biens ou de prestations de services')], limit=1)

    charcuterie = fields.Boolean(string="Charcuterie", default=False)
    volaille = fields.Boolean(string="Volaille", default=False)
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.user.company_id,
        required=False,
        string='Company'
    )
    date_at = fields.Date(required=True, string="A la Date",
                          default=fields.Date.context_today)
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries')],
                                   string='Target Moves',
                                   required=True,
                                   default='all')
    account_ids = fields.Many2many(
        comodel_name='account.account',
        string='Filtre des comptes', default=lambda self: self._default_account_get()
    )
    receivable_accounts_only = fields.Boolean(string=u"Comptes de revenus uniquement")
    payable_accounts_only = fields.Boolean(string=u"Comptes de depenses uniquement")
    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Filtre des partenaires',
    )
    show_move_line_details = fields.Boolean(string=u"Afficher les details de la ligne du mouvement")

    @api.onchange('company_id')
    def onchange_company_id(self):
        """Handle company change."""
        if self.company_id and self.partner_ids:
            self.partner_ids = self.partner_ids.filtered(
                lambda p: p.company_id == self.company_id or
                not p.company_id)
        if self.company_id and self.account_ids:
            if self.receivable_accounts_only or self.payable_accounts_only:
                self.onchange_type_accounts_only()
            else:
                self.account_ids = self.account_ids.filtered(
                    lambda a: a.company_id == self.company_id)
        res = {'domain': {'account_ids': [],
                          'partner_ids': []}}
        if not self.company_id:
            return res
        else:
            res['domain']['account_ids'] += [
                ('company_id', '=', self.company_id.id)]
            res['domain']['partner_ids'] += [
                '|', ('company_id', '=', self.company_id.id),
                ('company_id', '=', False)]
        return res

    @api.onchange('receivable_accounts_only', 'payable_accounts_only')
    def onchange_type_accounts_only(self):
        """Handle receivable/payable accounts only change."""
        if self.receivable_accounts_only or self.payable_accounts_only:
            domain = [('company_id', '=', self.company_id.id)]
            if self.receivable_accounts_only and self.payable_accounts_only:
                domain += [('internal_type', 'in', ('receivable', 'payable'))]
            elif self.receivable_accounts_only and (self.charcuterie or self.volaille):
                domain += [('internal_type', '=', 'receivable')]
            elif self.payable_accounts_only:
                domain += [('internal_type', '=', 'payable')]
            self.account_ids = self.env['account.account'].search(domain)
        else:
            self.account_ids = None

    @api.multi
    def button_export_html(self):
        self.ensure_one()
        if self.volaille == True and self.charcuterie == True:
                raise exceptions.ValidationError(_('Merci de cocher une seule case "Charcuterie" ou "Volaille" !'))
                return {
                    'warning': {'title': _('Error'), 'message': _('Error message'),},
            }
        action = self.env.ref(
            'account_financial_report.action_report_aged_partner_balance')
        vals = action.read()[0]
        context1 = vals.get('context', {})
        if isinstance(context1, pycompat.string_types):
            context1 = safe_eval(context1)
        model = self.env['report_aged_partner_balance']
        report = model.create(self._prepare_report_aged_partner_balance())
        report.compute_data_for_report()

        context1['active_id'] = report.id
        context1['active_ids'] = report.ids
        vals['context'] = context1
        return vals

    @api.multi
    def button_export_pdf(self):
        self.ensure_one()
        report_type = 'qweb-pdf'
        return self._export(report_type)

    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        report_type = 'xlsx'
        return self._export(report_type)

    def _prepare_report_aged_partner_balance(self):
        self.ensure_one()
        return {
            'date_at': self.date_at,
            'only_posted_moves': self.target_move == 'posted',
            'company_id': self.company_id.id,
            'charcuterie': self.charcuterie,
            'volaille': self.volaille,
            'filter_account_ids': [(6, 0, self.account_ids.ids)],
            'filter_partner_ids': [(6, 0, self.partner_ids.ids)],
            'show_move_line_details': self.show_move_line_details,
        }

    def _export(self, report_type):
        """Default export is PDF."""
        model = self.env['report_aged_partner_balance']
        report = model.create(self._prepare_report_aged_partner_balance())
        report.compute_data_for_report()
        return report.print_report(report_type)
    
    
    @api.onchange('charcuterie','volaille')
    @api.depends('charcuterie','volaille')
    def onchange_charcuterie(self):
        for record in self:
            record.account_ids = self.env['account.account'].search([('code', '=', '411100')])
            if record.charcuterie == True:
                partners = self.env['res.partner'].search([('customer','=',True),('Client_Charcuterie','=',True),('Client_GC','=',False)])
                record.partner_ids = partners
                
            elif record.volaille == True:
                partners = self.env['res.partner'].search([('customer','=',True),('Client_Volaille','=',True),('Client_GC','=',False)])
                record.partner_ids = partners
                
            elif record.volaille == True and record.charcuterie == True:
                raise exceptions.ValidationError(_('Merci de specifier le type Charcuterie ou Volaille !'))
                return {
                    'warning': {'title': _('Error'), 'message': _('Error message'),},
            }
                
            else:
                record.partner_ids = False
                
            
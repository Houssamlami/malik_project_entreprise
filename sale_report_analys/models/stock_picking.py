from odoo import tools
from odoo import api, fields, models
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta


class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    
    
    '''@api.depends('scheduled_date')
    def _get_date_tomorrow(self):
        for record in self:
            date = record.scheduled_date + relativedelta(days=-1)
            record.date_tomorow = date
            
            
    date_tomorow = fields.Datetime(compute='_get_date_tomorrow', string='Date', readonly=True)
    '''
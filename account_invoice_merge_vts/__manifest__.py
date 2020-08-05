{
    'name': "Account Invoice Merge",
    "category": "Account Invoice",
    'author': "Vraja Technologies",
    'license': 'AGPL-3',
    'summary':"""Merge Draft Account Invoice.""",
    'depends': [
        'account'
    ],
    'data': [
        'view/account_invoice_merge.xml',
    ],
    'test' :  [ ],
    'css'  :  [ ],
    'demo' :  [ ],
    'installable' : True,
    'application' :  False,
    "images":['static/description/merge_invoice.jpg'],
}

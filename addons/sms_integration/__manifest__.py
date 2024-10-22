{
    'name': "sms integration",
    'version': '1.0',
    'depends': ['base', 'sms'],
    'author': "Arash Mohammadi - Mohammad Gelimbaf",
    'category': '',
    'sequence':-100,
    'description': "this is a module for managing sms module using in Iran",
    'installable': True,
    'application':True,
    # data files always loaded at installation
    'data': [
        'views/sms_send_view.xml',
        'views/add_new_providers.xml',
        # 'views/add_new_short_codes.xml',
        'views/sms_actions.xml',
        'views/menu_items.xml',
        'security/ir.model.access.csv',
        ],
    # data files containing optionally loaded demonstration data
    'demo': [],
    
}

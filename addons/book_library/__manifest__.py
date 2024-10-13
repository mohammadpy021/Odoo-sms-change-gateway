{
    "name": "Library Management System",
    "summary": "to manage all your library transactions",
    "description": """    
    to manage all your library transactions
    """,
    "author": "OdooPro",
    "website": "https://google.com",
    "category": "Tools",
    "sequence": 95,
    "version": '1.0.0',
    "depends": [
        "base",
        "sms"
    ],
    "data": [
        "views/book_views.xml",
        "views/menu_items.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
}

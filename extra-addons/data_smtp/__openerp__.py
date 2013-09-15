{
  'name': 'Module for Data Importation',
  'version': '1.0',
  'category': 'Generic Modules/Others',
  'description': "Sample module for data importation.",
  'author': 'Tiny',
  'website': 'http://www.openerp.com',
  'depends': ['base'],
  'init_xml': [
      'product.product.csv',
      'res.partner.csv',
  ],
  'update_xml': [
  ],
  'update_xml': [],
  'installable': True,
  'active': False,
}

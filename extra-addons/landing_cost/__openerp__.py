# -*- coding: utf-8 -*-
{
    'name': 'Landing Cost',
    'version': '0.1',
    'author': 'Openlabs Technologies & Consulting (P) Limited',
    'category': 'Generic Modules/Accounting',
    'description': """What is landing/landed cost ?
=============================
Commonly, the total cost of a landed shipment including purchase price, 
freight, insurance, and other costs up to the port of destination. 
In some instances, it may also include the customs duties and other taxes 
levied on the shipment.

The approach to solving the problem:

These costs cannot be added to the supplier invoice for the 
following reasons:

  1. Mismatch with invoice sent by supplier. 
     Adding costs that are not present in the invoice/bill raised by
     the supplier will result in a mismatch leading to audit difficulties

  2. If there are expenses which are not to be paid to the supplier
     including them in the supplier invoice will result in a net credit
     being recorded against the supplier, which is more than the actual

The solution here:

    1. Allow account moves to be listed against a supplier invoice as 
    the components for landing cost. The relationship will be one 
    to many between the invoice and account-move as same cost being
    added to several supplier invoices will result in an exaggeration
    of cost. 

    2. Update the cost based on the cost division algorithm

    3. Some of the costs of shipping will only be available long after
    the purchase invoice is confirmed. So it should be possible to still 
    add costs and the L/C should be recomputed

Limitations:

    1. Only true costs, which have been paid for by the company is included
    in the landing cost calculation. Some of the costs like impact on 
    working capital etc. cannot be computed as they may not necessarily
    be financial transactions (account moves) in the ERP

Alternatives:

     The analytic module could also be used to address the problem.
""",
    'website': 'http://www.openlabs.co.in/',
    'depends': [
        'purchase',
        ],
    'update_xml': [
        'account.xml'
    ],
    'installable': True,
    'active': False,
    }

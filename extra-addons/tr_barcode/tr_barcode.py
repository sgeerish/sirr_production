# -*- coding: utf-8 -*-
from osv import fields, osv
import base64
try:
    from reportlab.graphics.barcode import createBarcodeDrawing, \
            getCodes
except :
    print "ERROR IMPORTING REPORT LAB"

def _get_code(self, cr, uid, context=None):
    """get availble code """
    return [(r, r) for r in getCodes()]

class tr_barcode(osv.osv):
    """ Barcode Class """
    _name = "tr.barcode"
    _description = "Barcode"
    _columns = {
        'code': fields.char('Barcode',size=256),
        'res_model':fields.char('Model',size=256),
        'res_id':fields.integer('Res Id'),
        'image': fields.binary('Data'),
        'width':fields.integer("Width",
                help="Leave Blank or 0(ZERO) for default size"),
        'hight':fields.integer("Hight",
                help="Leave Blank or 0(ZERO) for default size"),
        'hr_form':fields.boolean("Human Readable",
                help="To genrate Barcode In Human readable form"),
        'barcode_type':fields.selection(_get_code, 'Type')
    }
    def get_image(self, value, width, hight, hr, code='QR'):
        """ genrating image for barcode """
        options = {}
        if width:options['width'] = width
        if hight:options['hight'] = hight
        if hr:options['humanReadable'] = hr
        try:
            ret_val = createBarcodeDrawing(code, value=str(value), **options)
        except Exception, e:
            raise osv.except_osv('Error', e)
            
        return base64.encodestring(ret_val.asString('jpg'))
    
    def generate_image(self, cr, uid, ids, context=None):
        "button function for genrating image """
        if not context:
            context = {}

        for self_obj in self.browse(cr, uid, ids, context=context):
            image = self.get_image(self_obj.code,
                        code=self_obj.barcode_type or 'qrcode',
                        width=self_obj.width, hight=self_obj.hight,
                        hr=self_obj.hr_form)
            self.write(cr, uid, self_obj.id,
                {'image':image},context=context)
        return True
tr_barcode()

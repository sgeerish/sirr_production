# -*- coding: utf-8 -*-
##############################################################################
#
#    Tech Receptives, Open Source For Ideas
#    Copyright (C) 2009-TODAY Tech-Receptives Solutions Pvt. Ltd.
#                            (<http://www.techreceptives.com>)
#
#    For this class, special CREDIT : akretion and team
#    Based on Raphaël Valyi's base_external_referential module
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv
from osv import fields
from ConfigParser import ConfigParser
import copy
import threading
import pooler
from tools.translate import _
import netsvc

def reverse_dict(to_process_dict):
    
    result = {}
    
    return dict([(v,k) for k,v in to_process_dict.items()])

def get_mapping_fields(self, cr, uid, shop_id, context=None, reverse=False):
    
    result = {}
    
    if not context:
        context = {}
        
    shop_pool = self.pool.get('sale.shop')
    shop_data = shop_pool.read(cr, uid, shop_id, ['prestashop_config_path'])
    
    if not shop_data['prestashop_config_path'] or  \
       not shop_data['prestashop_config_path'].endswith(".conf") or\
       not self._prestashop:
        
        return result,False
    
    config = ConfigParser()
    config.read(shop_data['prestashop_config_path'])
    
    if not self._name in config.sections():
        return result,False
    
    mapping = dict(config.items(self._name))
    self._search_field = mapping.get('search_field','')
    result = eval(mapping['mapping'])
    
    mapping_func = {}
    
    if reverse:
        
        result = reverse_dict(result)
        mapping_func = mapping['import_field_function']
        
    else:
        
        mapping_func = mapping['export_field_function']
        
    record_name = eval(mapping["ext_record"])
    result['prestashop_record_name'] = record_name
    result['prestashop_read_mapping'] = mapping.get('read_mapping',False)
    
    if 'exclude_fields' in mapping:
        
        result['exclude_fields'] = mapping['exclude_fields']
        
    return result,mapping_func

def get_openerp_data(self, cr, uid, shop_id, presta_dicts, context=None):
    
    final_result = []
    
    if not context:
        
        context = {}
        
    if not self._prestashop or not presta_dicts:
        
        return final_result
    
    if not isinstance(presta_dicts, (list,tuple)):
        
        presta_dicts = [presta_dicts]
        
    rev_mapping,mapping_func = self.get_mapping_fields(cr, uid, shop_id,
                                                       context=context,
                                                       reverse=True)
    
    record_name = rev_mapping['prestashop_record_name']
    
    del rev_mapping['prestashop_record_name']
    del rev_mapping['prestashop_read_mapping']
    
    if context.get('read_at_once',False):
        
        presta_dicts = presta_dicts[0][self._prestashop_name]
        
        if record_name in presta_dicts:
            
            presta_dicts = presta_dicts[record_name]
            
    if not isinstance(presta_dicts,(list,tuple)):
        
        presta_dicts = [presta_dicts]
        
    for presta_dict in presta_dicts:
        
        result = {}
        
        if record_name in presta_dict:
            presta_dict = presta_dict[record_name]
        mapping_val = presta_dict
        
        try:
            mapping_value = eval(mapping_func)
            
        except Exception as e:
            
            print "ERROR IN EVAL",e,self._name
            self.pool.get(
               'prestashop.log').register_log(cr, uid, shop_id, self._name,
                  _("Erro in Eval of Openerp Data is %s" %e), 'error', 'import',
                                                             context=context )
            
            print mapping_func,mapping_val
            
        presta_dict.update(dict([(x,y) for x,y in mapping_value.items() \
                                       if x not in presta_dict]))
        
        for k,v in presta_dict.items():
            
            if k == 'id':
                result['ext_id'] = v
                
            if k not in rev_mapping:
                
                if k  in mapping_value:
                   result[k] = mapping_value[k]
                    
                continue

            result[rev_mapping[k]] = v
            
            if k in mapping_value:
                
                result[rev_mapping[k]] = mapping_value[k]
                
        final_result.append(result)

    return final_result

def get_updated_ids(self, cr, uid, shop_id, context={}):
    
    up_ids = []
    
    openerp_ids = self.search(cr, uid, [], context=context)
    shop_obj = self.pool.get('sale.shop').browse(cr, uid, shop_id,
                                                 context=context)
    
    if not shop_obj.last_sync_date:
        
        return openerp_ids

    for openerp_id in openerp_ids :
        
        ext_id = self.get_ext_ref(cr, uid, shop_id, openerp_id,
                                  context=context)
        if not ext_id:
            
            up_ids.append(openerp_id)
            continue
        
        ref_id = self.search(cr, uid, [
                '|',
                ('write_date','>',shop_obj.last_sync_date),
                ('create_date','>',shop_obj.last_sync_date),
                ('id','=',openerp_id)
        ])
        
        if ref_id:
            
            up_ids.append(openerp_id)

    return up_ids

def get_prestashop_data(self, cr, uid, shop_id, openerp_ids, context=None,
                        translation_fields=[]):
    
    final_result = []
    
    if not context:
        
        context = {}
        
    if not self._prestashop:
        
        return final_result
    
    if not isinstance(openerp_ids, (list,tuple)):
        
        openerp_ids = [openerp_ids]
        
    mapping,mapping_func = self.get_mapping_fields(cr, uid, shop_id,
                                                   context=context)
    
    record_name = mapping['prestashop_record_name']

    del mapping['prestashop_record_name']
    del mapping['prestashop_read_mapping']
    
    for self_obj in self.browse(cr, uid, openerp_ids, context=context):
        
        mapping_val = {}
        result = {}

        for k,v in mapping.items():
            if k in translation_fields:
                
                value = self._get_translation(cr, uid, shop_id, self_obj.id,
                                              k, getattr(self_obj,k),
                                              context=context)
                result[v] = value
                mapping_val[k] = value
                
                continue
            
            if k == 'exclude_fields':
                
                result[k] = v
                continue
            
            try:
                result[v] = getattr(self_obj,k)
                mapping_val[k] = getattr(self_obj,k)
                
            except:
                result[v] = False
                mapping_val[k] = False

        mapping_value = eval(mapping_func)
        result.update(
            dict([(mapping[x],mapping_value[x]) for x in mapping_value])
        )
#        for field in translation_fields:

        final_result.append({record_name: result})

    return final_result

def write_to_prestashop(self, cr, uid, shop_id, openerp_ids, vals,
                        context=None, convert_presta=False):
                        
    
    if not context:
        
        context = {}
        
    if not self._prestashop:
        
        return False
    
    if not isinstance(openerp_ids, (list,tuple)):
        
        openerp_ids = [openerp_ids]

    ret_val = False
    shop_pool = self.pool.get('sale.shop')
    ext_pool = self.pool.get('external.reference')
    ext_ids = []
    
    if convert_presta:
        ext_ids = [self.get_ext_ref(cr, uid, shop_id, openerp_id,
                                    context) for openerp_id in openerp_ids]
    else:
        ext_ids = openerp_ids

    connection = shop_pool.get_presta_shop(cr, uid, shop_id, context=context)
    
    if connection:
        ret_val = connection.write_prestashop(self._prestashop_name,
                                              ext_ids, vals)

    return ret_val

def create_to_prestashop(self, cr, uid, shop_id, openerp_id, vals={},
                         context=None):
    
    if not context:
        context = {}
        
    if not self._prestashop:
        return False
    
    ret_val = False
    
    if not vals:
        vals = self.get_prestashop_data(cr, uid, shop_id, openerp_id,
                                        context=context)
        
    shop_pool = self.pool.get('sale.shop')
    ext_pool = self.pool.get('external.reference')

    connection = shop_pool.get_presta_shop(cr, uid, shop_id, context=context)
    
    if connection:
        ret_val = connection.create_prestashop(self._prestashop_name, vals)
        
        for obj in  ret_val:
            
            if obj =='url':
                
                continue
            
            if 'id' in ret_val[obj]:
                
                self.set_ext_ref(cr, uid, shop_id, openerp_id,
                                 ret_val[obj]['id'], context)

    return ret_val


def read_from_prestashop(self, cr, uid, shop_id, openerp_ids, context=None,
                         convert_presta=False):
    
    if not context:
        context = {}
        
    if not self._prestashop:
        return False
    
    ret_val = []
    
    if not isinstance(openerp_ids, (list,tuple)):
        openerp_ids = [openerp_ids]
        
    shop_pool = self.pool.get('sale.shop')
    connection = shop_pool.get_presta_shop(cr, uid, shop_id, context=context)
    
    if convert_presta:
        ext_ids = [self.get_ext_ref(cr, uid, shop_id,
                                    openerp_id, context) \
                                    for openerp_id in openerp_ids]
        
    else:
        ext_ids = [openerp_id for openerp_id in openerp_ids]
        
    if connection and ext_ids:
        
        if context.get('read_at_once',False):
            
            rev_mapping,mapping_func = self.get_mapping_fields(cr, uid,
                                                               shop_id,
                                                               context=context,
                                                               reverse=True)
            
            read_mapping = rev_mapping.get('prestashop_read_mapping',False)
            
            if 'exclude_fields' in rev_mapping:
                del rev_mapping['exclude_fields']
                
            del rev_mapping['prestashop_record_name']
            del rev_mapping['prestashop_read_mapping']
            
            if read_mapping:
                
                options = {
                           'display':str(eval(read_mapping)+['id']).replace("'",
                                    "").replace("\n","").replace(" ","").strip()
                          }
                
            else:
                options = {
                           'display':str(rev_mapping.keys()+['id']).replace("'",
                                                                            "")
                           }
                
            ret_val = connection.read_prestashop(self._prestashop_name, ext_ids,
                                                 options=options,
                                                 all_fields=False)
        else:
            
            ret_val = connection.read_prestashop(self._prestashop_name, ext_ids)
            
    return ret_val

def search_from_prestashop(self, cr, uid, shop_id, presta_ids=[], context=None):
    
    if not context:
        context = {}
        
    if not self._prestashop:
        return False
    
    if not isinstance(presta_ids, (list,tuple)):
        presta_ids = [presta_ids]
        
    result = []

    shop_pool = self.pool.get('sale.shop')
    connection = shop_pool.get_presta_shop(cr, uid, shop_id, context=context)
    
    options = {}
    
    if presta_ids:
        
        options = {
                   'filter[id]':'[' +'|'.join( str(x) for x in presta_ids) + ']'
                  }

    res_val = connection.search_prestashop(self._prestashop_name,options)
    
    for res in res_val:
        
        if res_val[res]:
            check_dict = res_val[res][res_val[res].keys()[0]]
            
            if type(check_dict) == type({}):
                result = [int(check_dict['id'])]
            else:
                result = [int(x['id']) for x in check_dict]

    return result

def _get_translation(self, cr, uid, shop_id, openerp_id, field, value,
                     context={}):
    
    final_result = []
    
    lang_pool = self.pool.get('prestashop.lang')
    trans_pool = self.pool.get('ir.translation')
    
    for presta_lang_id in \
         self.pool.get('prestashop.lang').search(cr, uid, [], context=context):
                                                              
        
        data = lang_pool.read(cr, uid, [presta_lang_id], ['lang_id'],
                              context=context)[0]
        ext_id = lang_pool.get_ext_ref(cr, uid, shop_id, presta_lang_id,
                                       context=context)
        
        if not ext_id:
            continue
        
        lang_id = data['lang_id'] and data['lang_id'][0] or False
        
        if not lang_id:
            continue
        
        lang_code = self.pool.get('res.lang').browse(cr, uid, lang_id,).code
        
        if lang_code == 'en_US':
            trans = value
        else:
            trans = trans_pool._get_ids(cr,  uid, self._name+','+field,
                                    'model', lang_code, [openerp_id])
            trans = trans[openerp_id] and trans[openerp_id] or value

        result = {'id':str(ext_id), '_text':trans}
        
        final_result.append(result)


    return {'language':final_result}



def _conver_translation(self, cr, uid, shop_id, trans_data):
    
    result = {}
    
    if 'language' not in trans_data:
        
        return result
    
    if not isinstance(trans_data['language'], (list,tuple)):
        
        trans_data['language'] = [trans_data['language']]
        
    lang_pool = self.pool.get('prestashop.lang')
    
    for value in trans_data['language']:
        
        lang_id = lang_pool.get_int_ref(cr, uid, shop_id, value['id'],
                                        context= {'search_lang_id':True})
        
        if not lang_id:
            continue
        
        lang_code = self.pool.get('res.lang').browse(cr, uid, lang_id,).code
        result[lang_code] = value.get('_text','')
        
    return result

def export_to_prestashop(self, cr, uid, shop_id, ids, context={},
                         convert_presta=False):

    self.pool.get('prestashop.log').register_log(cr, uid, shop_id, self._name,
                                         _("Export Started"), 'info', 'export',
                                            context=context)                                             
    
    if getattr(self,'_not_thread',False) and self._not_thread:
        
        self.export_to_prestashop_thread(cr, uid, shop_id, ids, context,
                                         convert_presta, Thread=False)
        
    else:
        
        threaded_calculation = threading.Thread(
                                    target=self.export_to_prestashop_thread,
                                            args=(cr.dbname, uid, shop_id,
                                                  ids, context, convert_presta))                                                                                                     
        
        threaded_calculation.start()
        
    return True

def export_to_prestashop_thread(self, cr, uid, shop_id, ids, context={},
                         convert_presta=False, Thread=True):
    
    if not ids:
        return False
    
    if cr and Thread:
        cr = pooler.get_db(cr).cursor()
        
    context['lang'] = 'en_US'
    logger = netsvc.Logger()
    
    fields_get = self.fields_get(cr, uid,
                             context=context)
    
    fields_translate = [x for x in fields_get \
                        if fields_get[x].get('translate',False)]
    
    for  presta_data,openerp_id in \
         zip(self.get_prestashop_data(cr, uid, shop_id,ids, context=context,
                                      translation_fields=fields_translate),ids):
        
        presta_id = self.get_ext_ref(cr, uid, shop_id, openerp_id,
                                     context=context)
        
        if presta_id:
            
            presta_data = self.write_to_prestashop(cr, uid, shop_id, openerp_id,
                                                   presta_data, context,
                                                   convert_presta=True)
            
            if  not presta_data or 'errors' in presta_data:
                
                self.pool.get(
                    'prestashop.log').register_log(cr, uid, shop_id, self._name,
                      _("Error While writing External Record for" /
                     "object %s Openerp ID %s Error %s"%(self._name, openerp_id,
                                                         presta_data)), 'error',
                                                      'export', context=context)                                                        
                                                        
                cr.commit()
                
                continue
            
            self.pool.get(
                  'prestashop.log').register_log(cr, uid, shop_id,self._name,
                    _("Record Write for %s openerp id %s " /
                        "External id %s"%(self._name, openerp_id, presta_id)),
                                          'info', 'export', context=context)                                            
            
        else:
            
            presta_data = self.create_to_prestashop(cr, uid, shop_id,
                                                    openerp_id, presta_data,
                                                    context)
            
            if 'errors' in presta_data:
                
                self.pool.get(
                   'prestashop.log').register_log(cr, uid, shop_id,self._name,
                     _("Error While creating External Record for object %s " /
                        "Openerp ID %s Error %s"%(self._name,openerp_id,
                                              presta_data)), 'error', 'export',
                                              context=context)
                cr.commit()
                
                continue

            self.pool.get(
                  'prestashop.log').register_log(cr, uid, shop_id, self._name,
                         _("Record Created for %s openerp id %s " /
                           "External id %s"%(self._name, openerp_id,
                                             presta_data)), 'info', 'export',
                                             context=context)
                                                    
        cr.commit()

    if Thread:
        
        try:
            cr.close()
            
        except Exception:
            
            pass
        
    return True

def import_from_prestashop(self, cr, uid, shop_id, ids=[], context={},
                           convert_presta=False):
    
    if getattr(self,'_not_thread',False) and self._not_thread:
        
        self.import_from_prestashop_thread(cr, uid, shop_id, ids, context,
                                           convert_presta, Thread=False)
        
    else:
        
        threaded_calculation = threading.Thread(
                                target=self.import_from_prestashop_thread, 
                                        args=(cr.dbname, uid, shop_id, ids,
                                              context, convert_presta)
                                              )
        threaded_calculation.start()
        
    return True

def import_from_prestashop_thread(self, cr, uid, shop_id, ids=[], context={},
                           convert_presta=False, Thread=True):
    
    if Thread:

        if cr and Thread:
            cr = pooler.get_db(cr).cursor()
            
    logger = netsvc.Logger()
    
    if not ids:
        
        ids = self.search_from_prestashop(cr, uid, shop_id, context=context)
        convert_presta = False
        
    read_preasta_datas = self.read_from_prestashop(cr, uid, shop_id, ids,
                                             context=context,
                                             convert_presta=convert_presta)
    
    trans_pool = self.pool.get('ir.translation')
    fields_get = self.fields_get(cr, uid,
                                 context=context)
    
    for openerp_data in self.get_openerp_data(cr,uid, shop_id,
                                              read_preasta_datas,
                                              context=context):

        presta_id = openerp_data['ext_id']
        other_trans = []

        fields_translate = [x for x in fields_get \
                            if fields_get[x].get('translate',False) and x \
                            in openerp_data.keys()]
        
        for field in fields_translate:

            translations = self._conver_translation(cr, uid,
                                                    shop_id,
                                                    openerp_data[field])
            
            openerp_data[field] = translations['en_US']
            other_trans.append((translations, field))

        new_cnt = copy.deepcopy(context)
        search_field = self._search_field
        
        if search_field:
            
            try:
                new_cnt['search_prestashop_data'] = eval(search_field)
                
            except Exception as e:
                
                logger.notifyChannel(_("Prestashop Sync"), netsvc.LOG_ERROR,
                                     _("Erro in Eval of search field"))
                self.pool.get(
                   'prestashop.log').register_log(cr, uid, shop_id, self._name,
                             _("Erro in Eval of search field Error is %s" %e),
                                         'error', 'import', context=context)
                                                            

        openerp_id = self.get_int_ref(cr, uid, shop_id,
                                      openerp_data['ext_id'], context=new_cnt)
        
        if openerp_id:
            
            ext_id = openerp_data['ext_id']
            del openerp_data['ext_id']
            
            try:
                
                self.write(cr, uid, [openerp_id], openerp_data, context=context)
                self.pool.get(
                  'prestashop.log').register_log(cr, uid, shop_id, self._name,
                            _("Record Write for %s openerp id %s " /
                              "External id %s"%(self._name,openerp_id, ext_id)),
                                             'info', 'import', context=context)
                
                cr.commit()
                
            except Exception as e:

                self.pool.get(
                    'prestashop.log').register_log(cr, uid, shop_id, self._name,
                                    _("Error in writing to %s Values are %s" /
                                        "error is %s"%(self._name, openerp_data,
                                                        e)), 'error', 'import',
                                                             context=context)
                                                           
                cr.commit()
                
                continue
        else:
            
            try:
                
                ext_id = openerp_data['ext_id']
                del openerp_data['ext_id']
                
                openerp_id = self.create(cr, uid, openerp_data, context=context)
                
                cr.commit()
                
                self.pool.get(
                  'prestashop.log').register_log(cr, uid, shop_id, self._name,
                                        _("Record created for %s openerp id %s"/
                                      " External id %s"%(self._name, openerp_id,
                                                     ext_id)), 'info', 'import',
                                                     context=context)
            except Exception as e:
                
                self.pool.get(
                    'prestashop.log').register_log(cr, uid, shop_id, self._name,
                                 _("Error in Creating new %s Values are %s" / 
                                   "error is %s"%(self._name, openerp_data, e)),
                                             'error', 'import', context=context)
                                                                            
                cr.commit()
                
                continue
            
        self.set_ext_ref(cr, uid, shop_id, openerp_id, presta_id, context)
        
        for trans_data,field in other_trans:
            
            for lang_data in trans_data:
                
                if lang_data == 'en_US':
                    
                    continue
                
                trans_pool._set_ids(cr, uid, self._name+','+field,
                                    'model',lang_data,[openerp_id],
                                    trans_data[lang_data],openerp_data[field],
                )
                
        cr.commit()
        
    if Thread:
        
        try:
            cr.close()
            
        except Exception:
            pass
        
    return True

class external_reference(osv.osv):
    
    _name = 'external.reference'
    _rec_name = "res_model,res_id"

    _columns = {
                'res_model':fields.char('Model', size=64),
                'res_id':fields.integer('Res Id'),
                'external_reference_id':fields.many2one('sale.shop', 
                                                        'External Reference'),
                'ext_id':fields.integer('External Id'),
                'create_date':fields.datetime('Create Date'),
                'write_date':fields.datetime('Write Date'),
                }

external_reference()

class preshashop_log(osv.osv):
    
    _name = 'prestashop.log'
    _description = 'Prestashop Log'

    _columns = {
                'create_date':fields.datetime('Created Date'),
                'user_id':fields.many2one('res.users', 'User'),
                'shop_id':fields.many2one('sale.shop', 'Shop',
                                          help="Select your shop name"),
                'state':fields.selection([
                                          ('info','Info'),
                                          ('error','Error')                                          
                                         ],'State'),
                'res_model':fields.char('Model', size=256),
                'sync_type':fields.selection([
                                              ('import','Import'),
                                              ('export','Export')
                                             ],'Sync Type'),
                'msg':fields.text('Message'),
                }
    
    def register_log(self, cr, uid, shop_id, res_model, msg, state, sync_type,
                     context={}):
        
        self.create(cr, uid, {
                              'user_id':uid,
                              'shop_id':shop_id,
                              'res_model':res_model,
                              'msg':msg,
                              'state':state,
                              'sync_type':sync_type,
                             })

        return True

preshashop_log()

def unlink(self, cr, uid, ids, context={}):
    
    res = super(osv.osv, self).unlink(cr, uid, ids, context=context)
    
    if not getattr(self,'_prestashop',False):
        
        return res
    
    for openerp_id in ids:
        
        ref_pool = self.pool.get('external.reference')
        ref_ids = ref_pool.search(cr, uid, [
                    ('res_model','=', self._name),
                    ('res_id', '=', openerp_id),
                ])
        
        if ref_ids:
            
            ref_pool.unlink(cr, uid, ref_ids, context=context)
            
    return res

def set_ext_ref(self, cr, uid, external_reference_id, openerp_id, presta_id,
                context={}):
    
    ref_pool = self.pool.get('external.reference')
    
    ref_ids = ref_pool.search(cr, uid, [
                ('res_model','=', self._name),
                ('res_id', '=', openerp_id),
                ('external_reference_id', '=', external_reference_id),
            ])
    
    if ref_ids:
        
        ref_pool.write(cr, uid, ref_ids, {'ext_id':presta_id})
        
    else:
        
        ref_pool.create(cr, uid, {
                                  'res_model':self._name,
                                  'res_id':openerp_id,
                                 'external_reference_id':external_reference_id,
                                  'ext_id':presta_id,
                                  })

    return True

def get_ext_ref(self, cr, uid, external_reference_id, openerp_id, context={}):
    
    presta_id = False

    ref_pool = self.pool.get('external.reference')
    ref_ids = ref_pool.search(cr, uid, [
                ('res_model','=', self._name),
                ('res_id', '=', openerp_id),
                ('external_reference_id', '=', external_reference_id),
            ])
    
    if ref_ids:
        
        ref_data = ref_pool.read(cr, uid, ref_ids,['ext_id'],
                                 context=context)[0]
        presta_id = ref_data['ext_id']

    return presta_id

def get_int_ref(self, cr, uid, external_reference_id, presta_id, context={}):
    
    openerp_id = False
    
    ref_pool = self.pool.get('external.reference')
    ref_ids = ref_pool.search(cr, uid, [
                ('res_model','=', self._name),
                ('ext_id', '=', presta_id),
                ('external_reference_id', '=', external_reference_id),
            ])
    
    if ref_ids:
        
        ref_data = ref_pool.read(cr, uid, ref_ids, ['res_id'],
                                 context=context)[0]
        openerp_id = ref_data['res_id']
        
    if not openerp_id and context.get('search_prestashop_data'):
        
        openerp_id = self.search(cr, uid, context.get('search_prestashop_data'),
                                 context=context)
        
        if openerp_id:
            openerp_id = openerp_id[0]

    return openerp_id

osv.osv.write_to_prestashop = write_to_prestashop
osv.osv.create_to_prestashop = create_to_prestashop
osv.osv.read_from_prestashop = read_from_prestashop
osv.osv.search_from_prestashop = search_from_prestashop
osv.osv.set_ext_ref = set_ext_ref
osv.osv.get_ext_ref = get_ext_ref
osv.osv.get_int_ref = get_int_ref
osv.osv.get_mapping_fields = get_mapping_fields
osv.osv.get_openerp_data = get_openerp_data
osv.osv.get_prestashop_data = get_prestashop_data
osv.osv._conver_translation = _conver_translation
osv.osv.import_from_prestashop = import_from_prestashop
osv.osv.import_from_prestashop_thread = import_from_prestashop_thread
osv.osv.unlink = unlink
osv.osv.export_to_prestashop = export_to_prestashop
osv.osv.export_to_prestashop_thread = export_to_prestashop_thread
osv.osv._get_translation = _get_translation
osv.osv.get_updated_ids = get_updated_ids

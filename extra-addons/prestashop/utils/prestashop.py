# -*- coding: utf-8 -*-
##############################################################################
#
#    Tech Receptives, Open Source For Ideas
#    Copyright (C) 2009-TODAY Tech-Receptives Solutions Pvt. Ltd.
#                            (<http://www.techreceptives.com>)
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

import requests
import urllib
import utils
import logging
import copy

def get(shop_data, context=None):

    return prestashop(*shop_data, context=context)

class prestashop(object):

    def __init__(self, server_url, server_key, debug=False, validate=True,
                 context=None):

            if context is None:
                context = {}
                
            self.server_url = server_url
            self.server_key = server_key

            if not self.server_url.endswith('/'):
                self.server_url += '/'

            if not self.server_url.endswith('/api/'):
                self.server_url += 'api/'

            self.debug = debug
            self.validate = validate
            self.context = context
            
    def test_connection(self):

        return self._process_response(requests.get(self.server_url,
                                                   auth=(self.server_key,'')))


    def register_log(self, msg, type='info'):
        
        if self.debug:
            
            logging.debug("%s", msg)
            
        if type=='error':
            
            logging.error(msg)
            
            #TODO Log for Openerp Debug

    def _process_response(self, res_presta):
        
        print "res",res_presta.url
        
        if not res_presta.content:
            
            if not res_presta.ok:
                
                return False
            
            return True
        
        if res_presta.ok:
            
            info_dict = self._convert_to_dict(res_presta.content)['prestashop']
            new_dict = copy.deepcopy(info_dict)
            
            info_dict.update({
                              'url': res_presta.url                              
                              })
            
            self.register_log(info_dict, type='info')
            
            return new_dict
        
        if res_presta.status_code == 404:
            
            return {'errors':{'error':{
                                       'message': 'Error 404 Page Not Found'
                                       }}}
        
        error_dict = self._convert_to_dict(
                                    res_presta.content).get('prestashop', False)
        if not error_dict:
            
            error_dict = self._convert_to_dict(res_presta.content)
            
        error_dict.update({
                           'url':res_presta.url
                           })
        
        self.register_log(error_dict,type='error')
        
        return error_dict


    def _convert_to_dict(self, data):
        
        return utils.ConvertXmlToDict(data)

    def _convert_to_xml(self, xml_data):
        
        return utils.ConvertDictToXml(xml_data)

    def convert_options(self, options):
        
        if self.debug:
            options.update({
                            'debug': True
                            })
            
        return urllib.urlencode(options)

    def process_reponse(self, response):

        return True

    def create_image(self, resource, obj, res_id, data):
        
        url = self.server_url + '%s/%s/%s/'%(resource,obj, res_id)
        rest = requests.post(url, files=data, auth=(self.server_key,''))
        
        return rest

    def get_image_data(self, resource, obj, res_id, img_id):
        
        url = self.server_url + '%s/%s/%s/%s'%(resource, obj, res_id, img_id)
        rest = requests.get(url, auth=(self.server_key,''))
        
        return rest

    def get_images_only(self, resource, obj, res_id):
        
        url = self.server_url + '%s/%s/%s/'%(resource, obj, res_id)
        rest = requests.get(url, auth=(self.server_key,''))
        
        return rest

    def get_images(self, resource, obj, res_id):
        
        url = self.server_url + '%s/%s/%s/'%(resource,obj,res_id)
        rest = self._process_response(
                                  requests.get(url, auth=(self.server_key, '')))
        
        return rest
    
    def get_image_ids(self, resource, obj):
        
        url = self.server_url + '%s/%s/'%(resource,obj)
        rest = self._process_response(
                                  requests.get(url, auth=(self.server_key,'')))
        
        return rest

    def delete_images(self, resource, obj, res_id,image_id=[]):
        
        if image_id:
            
            url = self.server_url + '%s/%s/%s/%s'%(resource, obj, res_id,
                                                   image_id)
        else:
            url = self.server_url +'%s/%s/%s'%(resource,obj,res_id)
            
        rest = self._process_response(
                                requests.delete(url, auth=(self.server_key,'')))
        
        return rest

    def create_prestashop(self, resource, data):

        if 'prestashop' not in data:
            data = {'prestashop':data}

        data = self._convert_to_xml(data)
        url = self.server_url + '%s/'%resource
        rest = self._process_response(requests.post(url, data={'xml': data },
                                                    auth=(self.server_key,'')))
        
        return rest

    def write_prestashop(self, resource, ext_ids, data):
        
        if not isinstance(ext_ids, (list,tuple)):
            
            ext_ids = [ext_ids]
            
        rest = False

        for ext_id in ext_ids:
            new_data = data

            read_data = self.read_prestashop(resource, ext_id)
            
            if read_data:
                
                for f in eval(data[data.keys()[0]].get('exclude_fields',"[]")):
                    
                    if f in read_data[0][read_data[0].keys()[0]]:
                        del read_data[0][read_data[0].keys()[0]][f]
                        
                if 'exclude_fields' in data[data.keys()[0]]:
                    del data[data.keys()[0]]['exclude_fields']

                read_data[0][read_data[0].keys()[0]].update(data[data.keys()[0]])
                
                new_data = read_data[0]
                
                if 'prestashop' not in new_data:
                    new_data = {'prestashop':new_data}

                new_data = self._convert_to_xml(new_data)
                new_data = '<?xml version="1.0" encoding="UTF-8"?>' + new_data
                
                url = self.server_url + '%s/'%resource
                url += "%s"%ext_id
                
                rest = self._process_response(
                      requests.put(url, data=new_data, auth=(self.server_key,'')
                                   ))
                
        return rest

    def unlink_prestashop(self, resource, ext_ids):
        
        if not isinstance(ext_ids,(list,tuple)):
            ext_ids = [ext_ids]
            
        for ext_id in ext_ids:
            
            url = self.server_url + '%s/'%resource
            url += "%s"%ext_id
            
            rest = self._process_response(
                              requests.delete(url, auth=(self.server_key,'')))
            
        return rest

    def _convert_to_single_dict(self, resource, data):
        
        result = data['prestashop'].get(resource, False)
        
        return result

    def search_prestashop(self, resource, options):

        result = []

        url = self.server_url + '%s/'% (resource)
        
        if options:
            
            options_str = self.convert_options(options)
            url = url + '?%s'% (options_str,)
            
        res_presta = self._process_response(
                                requests.get(url, auth=(self.server_key,'')))

        return res_presta

    def read_prestashop(self, resource, ext_ids, options=None, all_fields=True):
        
        result = []
        list_not_flg = False

        if not isinstance(ext_ids,(list,tuple)):
            
            ext_ids = [ext_ids]
            
        url = self.server_url + '%s/'% (resource)
        
        if  not all_fields:
            
            ext_ids = [str(t) for t in ext_ids]
            options['filter[id]']=('['+'|'.join(ext_ids)+']').replace("'","")
            
            return self.search_prestashop(resource, options)
        
        result = []
        
        for ext_id in ext_ids:
            
            new_url = url + '%s'%ext_id
            res_presta = self._process_response(
                               requests.get(new_url, auth=(self.server_key,'')))
            if res_presta:
                
                result.append(res_presta)
                
        return result



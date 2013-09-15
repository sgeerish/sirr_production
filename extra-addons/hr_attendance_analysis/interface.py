# -*- encoding: utf-8 -*-
##############################################################################
#
#    Clock Reader for OpenERP
#    Copyright (C) 2004-2009 Moldeo Interactive CT
#    (<http://www.moldeointeractive.com.ar>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import timeutils as tu

class Interface(object):
    def __init__(self, cr, uid, pool, oid, otype):
        self._parms  = (cr, uid, pool)
        self._cache = pool.get(otype).read(cr, uid, oid)
        self._field = pool.get(otype).fields_get(cr, uid)
	self._local_cache = {}

    def __getitem__(self, name):
        if name in self._local_cache:
            return self._local_cache[name]
        if name in self._cache:
            ret = self._cache[name]
            if isinstance(ret, bool): return ret
            field = self._field[name]
            if field['type'] in ['char','int','float', 'selection']:
                _r = ret
            elif field['type'] in ['datetime']:
                _r = tu.dt(ret)
            elif field['type'] in ['date']:
                _r = tu.d(ret)
            elif field['type'] in ['many2one']:
                _r = Interface(*(self._parms + (ret[0] ,field['relation'])))
            elif field['type'] in ['many2many', 'one2many']:
                _r = map(lambda a: Interface(*(self._parms + a))
                           , zip(ret, [field['relation']]*len(ret)))
            else:
                raise NotImplementedError, \
                    "Not implemented for %s of type %s (%s)." % (name,
                                                                 field['type'],
                                                                str(ret))
            self._local_cache[name] = _r
            return _r
        else:
            # raise ValueError, "Not exists %s in object." % name
            return False

    def __getattr__(self, name):
        return self[name]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

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

from clock_f5 import Clock_F5
from clock_zkem import Clock_Zkem

# Here append more models

models = {
    'f5': ('F-5', Clock_F5),
    'Zkem': ('Zkem', Clock_Zkem),
}

labels = [ (k, l) for k, (l, c) in models.items() ]

classes = dict([(k, c) for k, (l, c) in models.items() ])

default = 'Zkem'


<?php
##############################################################################
#
#    Copyright (C) 2010-TODAY Tech Receptives (<http://www.techreceptives.com>).
#   
#    Authors : Kinner Vachhani  (Tech Receptives)
#    Concept : Parthiv Patel (Tech Receptives)
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

class Openerp extends Module
{
    function __construct(){
        $this->name = 'openerp';
        parent::__construct();

        $this->tab = 'Openerp Prestashop';
        $this->version = '0.1.0';
        $this->displayName = $this->l('Openerp Synchronization by Njconsultancy');
        $this->description = $this->l('This module synchronize openerp with Prestashop');
    }
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


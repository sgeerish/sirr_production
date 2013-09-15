# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 Smartmode LTD (<http://www.smartmode.co.uk>).
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
{
    "name" : "Currency Rates Updater",
    "version" : "1.0",
    "category" : "Tools",
    "depends" : [
                "base",
                "account",
                ],
    "author" : "SmartMode LTD",
    "description": '''This is a module developed at Smartmode for automatic currency updates from Yahoo.

Can be set to daily, weekly, monthly updates as required. To setup:

1 Ensure your currency codes are configured as per the ISO 4217. Example - CNY not RMB, KES, not KSH. Delete the ones that are with one or two characters.
2 Ensure your main company currency is set as base with the rate of 1. Or with the standard instalation, locate the EUR currency and mark it as base.
3 Install the module. Upon the first instaltion, the currency rates will get updated.
4 Navigate to Administration > Configuration > Scheduler and find the currency rate updated from the cron list to adjust the time to suit.

The module will keep a log of daily runs in the OpenERP res_log.''',
    "website" : "http://www.smartmode.co.uk/",
    "category" : "Accounting",
    "init_xml" : [],
    "update_xml" : [
                    "currency_data.xml",
                    ],
    "demo_xml" : [],
    "installable": True,
    "active" : False,
}

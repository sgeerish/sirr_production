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

#TODO replace query with printf. 
#TODO Include roll back facility on mysql error. Merge update and create category into one
#TODO Merge Product update and create into a single one
#TODO Implement Expection Handling

include("xmlrpcutils/xmlrpc.inc.php");
include("xmlrpcutils/xmlrpcs.inc.php");
include("../../config/settings.inc.php");

function debug($s){
    $fp = fopen("/tmp/debug.xmlrpc.txt","a");
    fwrite($fp, $s."\n");
    fclose($fp);
}

function getTest(){
    debug("It works");    
    return new xmlrpcresp( new xmlrpcval('90', 'int'));
}

/*
sample datastructure
$cat_data = {'category':{}, 'translation':{1:{}}}
*/

function create_category($cat_data){

        $con = mysql_connect(_DB_SERVER_, _DB_USER_, _DB_PASSWD_);
        if (!$con){
          die("Could not connect to server "._DB_SERVER_." : " . mysql_error());
        }
        mysql_select_db(_DB_NAME_, $con);

        $today = date('Y-m-d H:i:s', time());
        mysql_query("START TRANSACTION");
        mysql_query("INSERT INTO "._DB_PREFIX_."category (active,id_parent,level_depth,date_add,date_upd)
                VALUES ({$cat_data['category']['active']},
                        {$cat_data['category']['id_parent']},
                        {$cat_data['category']['level_depth']},
                        '{$today}',
                        '{$today}'
                        )");
        $id = mysql_insert_id();

        mysql_query("INSERT INTO "._DB_PREFIX_."category_group (id_category, id_group)
                VALUES ($id,
                        '1'
                        )");
        foreach($cat_data['translation'] as $lang_id => $lang_data ){
            mysql_query("INSERT INTO "._DB_PREFIX_."category_lang (id_lang, id_category, name, description, link_rewrite, meta_title, meta_keywords, meta_description)
                VALUES ({$lang_id},
                        {$id},
                        '{$lang_data['name']}',
                        '{$lang_data['description']}',
                        '{$lang_data['link_rewrite']}',
                        '{$lang_data['meta_title']}',
                        '{$lang_data['meta_keywords']}',
                        '{$lang_data['meta_description']}'
                        )");
        }
        mysql_query("COMMIT");

    return new xmlrpcresp( new xmlrpcval($id, 'int'));
}

function update_category($cat_data){
    $con = mysql_connect(_DB_SERVER_, _DB_USER_, _DB_PASSWD_);
        if (!$con){
          die("Could not connect to server "._DB_SERVER_." : " . mysql_error());
        }
        mysql_select_db(_DB_NAME_, $con);

        $today = date('Y-m-d H:i:s', time());
        mysql_query("START TRANSACTION");
        mysql_query("UPDATE "._DB_PREFIX_."category SET 
                    active = '{$cat_data['category']['active']}',
                    id_parent = '{$cat_data['category']['id_parent']}',
                    level_depth = '{$cat_data['category']['level_depth']}',
                    date_upd = '{$today}'
                    WHERE id_category = '{$cat_data['category']['id_category']}'
                    ");
        $id = $cat_data['category']['id_category'];

        mysql_query("DELETE FROM "._DB_PREFIX_."category_group WHERE id_category='{$cat_data['category']['id_category']}'");

        mysql_query("INSERT INTO "._DB_PREFIX_."category_group (id_category,id_group) VALUES 
                                ('{$cat_data['category']['id_category']}',
                                 '1')");

        foreach($cat_data['translation'] as $lang_id => $lang_data ){
            mysql_query("UPDATE "._DB_PREFIX_."category_lang SET 
                id_lang = {$lang_id},
                name = '{$lang_data['name']}',
                description = '{$lang_data['description']}',
                link_rewrite = '{$lang_data['link_rewrite']}',
                meta_title = '{$lang_data['meta_title']}',
                meta_keywords = '{$lang_data['meta_keywords']}',
                meta_description = '{$lang_data['meta_description']}'
                WHERE id_category = '{$cat_data['category']['id_category']}' AND id_lang = 1
                        ");
        }
        mysql_query("COMMIT");
    return new xmlrpcresp(new xmlrpcval($id,'int'));
}

/*
    product structure: {openerp_id:{'product':{},'translation':{}}}
*/
function create_product($prod_data){
        
        $return_data = array();
        $create_arr = array();
        $error_arr = array();

        $con = mysql_connect(_DB_SERVER_, _DB_USER_, _DB_PASSWD_);
        if(!$con){
          die("Could not connect to server "._DB_SERVER_." : " . mysql_error());
        }

        mysql_select_db(_DB_NAME_, $con);

        foreach($prod_data as $openerp_id => $prod_data){
            $today = date('Y-m-d H:i:s', time());
            mysql_query("START TRANSACTION");

            //Product entry in table
            mysql_query("INSERT INTO "._DB_PREFIX_."product (id_tax, id_manufacturer, id_supplier, id_category_default, id_color_default, quantity, price, wholesale_price, reduction_price, reduction_percent, reduction_from, reduction_to, on_sale, ecotax, reference, supplier_reference, location, weight, out_of_stock, quantity_discount, customizable, uploadable_files, text_fields, active, indexed, ean13, date_add, date_upd)
                VALUES ('{$prod_data['product']['id_tax']}',
                        '{$prod_data['product']['id_manufacturer']}',
                        '{$prod_data['product']['id_supplier']}',
                        '{$prod_data['product']['id_category_default']}',
                        '{$prod_data['product']['id_color_default']}',
                        '{$prod_data['product']['quantity']}',
                        '{$prod_data['product']['price']}',
                        '{$prod_data['product']['wholesale_price']}',
                        '{$prod_data['product']['reduction_price']}',
                        '{$prod_data['product']['reduction_percent']}',
                        '{$prod_data['product']['reduction_from']}',
                        '{$prod_data['product']['reduction_to']}',
                        '{$prod_data['product']['on_sale']}',
                        '{$prod_data['product']['ecotax']}',
                        '{$prod_data['product']['reference']}',
                        '{$prod_data['product']['supplier_reference']}',
                        '{$prod_data['product']['location']}',
                        '{$prod_data['product']['weight']}',
                        '{$prod_data['product']['out_of_stock']}',
                        '{$prod_data['product']['quantity_discount']}',
                        '{$prod_data['product']['customizable']}',
                        '{$prod_data['product']['uploadable_files']}',
                        '{$prod_data['product']['text_fields']}',
                        '{$prod_data['product']['active']}',
                        '{$prod_data['product']['indexed']}',
                        '{$prod_data['product']['ean13']}',
                        '{$today}',
                        '{$today}'
                        )");
            $record_id = mysql_insert_id();

            //Translation data
            foreach($prod_data['translation'] as $lang_id => $lang_data ){
                debug("helloo...".debug($lang_data['description']));
                mysql_query("INSERT INTO "._DB_PREFIX_."product_lang (id_lang,id_product,description,description_short,
                        meta_description,meta_keywords,meta_title,
                        link_rewrite,name,available_now,available_later) 
                    VALUES ('{$lang_id}',
                            '{$record_id}',
                            '{$lang_data['description']}',
                            '{$lang_data['description_short']}',
                            '{$lang_data['meta_description']}',
                            '{$lang_data['meta_keywords']}',
                            '{$lang_data['meta_title']}',
                            '{$lang_data['link_rewrite']}',
                            '{$lang_data['name']}',
                            '{$lang_data['available_now']}',
                            '{$lang_data['available_later']}'
                            )");
                }

            mysql_query("DELETE FROM "._DB_PREFIX_."accessory WHERE id_product_1 = $record_id");
            mysql_query("DELETE FROM "._DB_PREFIX_."pack WHERE id_product_pack = $record_id");
            
            //category insertion
            mysql_query("DELETE FROM "._DB_PREFIX_."category_product WHERE id_product = $record_id");
            
            mysql_query("INSERT INTO "._DB_PREFIX_."category_product (id_category, id_product, position)
		    VALUES (1,$record_id,0),({$prod_data['product']['id_category_default']},{$record_id},0)");
            
            #TODO Create a index for product
            mysql_query("UPDATE "._DB_PREFIX_."product SET indexed = 1 WHERE id_product = $record_id");
            
            if($record_id){
                mysql_query("COMMIT");
                $created_err[$openerp_id] = new xmlrpcval ($record_id, 'int');
            }
            else{
                mysql_query("ROLLBACK");
                array_push($error_arr, new xmlrpcval($record_id, 'int'));
            }
        }

    $return_data['created'] = new xmlrpcval($created_err, 'struct');
    $return_data['error'] = new xmlrpcval($error_arr, 'struct');

    return new xmlrpcresp( new xmlrpcval($return_data, 'struct'));
}

function update_product($up_data){

        $return_ids = array();
        $con = mysql_connect(_DB_SERVER_, _DB_USER_, _DB_PASSWD_);
        if(!$con){
          die("Could not connect to server "._DB_SERVER_." : " . mysql_error());
        }

        mysql_select_db(_DB_NAME_, $con);
        $return_data = array();
        foreach($up_data as $openerp_id => $prod_data){
            $today = date('Y-m-d H:i:s', time());
            mysql_query("START TRANSACTION");
            //Product entry in table
            mysql_query("UPDATE "._DB_PREFIX_."product SET 
                        id_tax = '{$prod_data['product']['id_tax']}',
                        id_manufacturer = '{$prod_data['product']['id_manufacturer']}',
                        id_supplier = '{$prod_data['product']['id_supplier']}',
                        id_category_default = '{$prod_data['product']['id_category_default']}',
                        id_color_default = '{$prod_data['product']['id_color_default']}',
                        quantity = '{$prod_data['product']['quantity']}',
                        price = '{$prod_data['product']['price']}',
                        wholesale_price = '{$prod_data['product']['wholesale_price']}',
                        reduction_price = '{$prod_data['product']['reduction_price']}',
                        reduction_percent = '{$prod_data['product']['reduction_percent']}',
                        reduction_from = '{$prod_data['product']['reduction_from']}',
                        reduction_to = '{$prod_data['product']['reduction_to']}',
                        on_sale = '{$prod_data['product']['on_sale']}',
                        ecotax = '{$prod_data['product']['ecotax']}',
                        reference = '{$prod_data['product']['reference']}',
                        supplier_reference = '{$prod_data['product']['supplier_reference']}',
                        location = '{$prod_data['product']['location']}',
                        weight = '{$prod_data['product']['weight']}',
                        out_of_stock = '{$prod_data['product']['out_of_stock']}',
                        quantity_discount = '{$prod_data['product']['quantity_discount']}',
                        customizable = '{$prod_data['product']['customizable']}',
                        uploadable_files = '{$prod_data['product']['uploadable_files']}',
                        text_fields = '{$prod_data['product']['text_fields']}',
                        active = '{$prod_data['product']['active']}',
                        indexed = '{$prod_data['product']['indexed']}',
                        ean13 = '{$prod_data['product']['ean13']}',
                        date_upd = '{$today}'
                        WHERE id_product = '{$prod_data['product']['id_product']}'");
            
            //Translation data
            foreach($prod_data['translation'] as $lang_id => $lang_data ){

                mysql_query("UPDATE "._DB_PREFIX_."product_lang SET
                            id_lang = '{$lang_id}',
                            id_product = '{$prod_data['product']['id_product']}',
                            description = '{$lang_data['description']}',
                            description_short = '{$lang_data['description_short']}',
                            meta_description = '{$lang_data['meta_description']}',
                            meta_keywords = '{$lang_data['meta_keywords']}',
                            meta_title = '{$lang_data['meta_title']}',
                            link_rewrite = '{$lang_data['link_rewrite']}',
                            name = '{$lang_data['name']}',
                            available_now = '{$lang_data['available_now']}',
                            available_later = '{$lang_data['available_later']}'
                            WHERE id_product = '{$prod_data['product']['id_product']}' AND id_lang = {$lang_id}
                            ");
                }
            debug(mysql_error());
            mysql_query("DELETE FROM "._DB_PREFIX_."accessory WHERE id_product_1 = {$prod_data['product']['id_product']}");
            mysql_query("DELETE FROM "._DB_PREFIX_."pack WHERE id_product_pack = {$prod_data['product']['id_product']}");
            
            //category insertion
            mysql_query("DELETE FROM "._DB_PREFIX_."category_product WHERE id_product = {$prod_data['product']['id_product']}");
            
            mysql_query("INSERT INTO "._DB_PREFIX_."category_product (id_category, id_product, position)
		        VALUES (1,{$prod_data['product']['id_product']},0),
                ({$prod_data['product']['id_category_default']},{$prod_data['product']['id_product']},0)");
            
            mysql_query("UPDATE "._DB_PREFIX_."product SET indexed = 1 WHERE id_product = {$prod_data['product']['id_product']}");
            mysql_query("COMMIT");

            array_push($return_ids, new xmlrpcval($openerp_id, 'int'));
        }

    return new xmlrpcresp( new xmlrpcval($return_ids, 'array'));
}

function getTaxes(){

        $con = mysql_connect(_DB_SERVER_, _DB_USER_, _DB_PASSWD_);
        if (!$con){
          die("Could not connect to server "._DB_SERVER_." : " . mysql_error());
        }
        mysql_select_db(_DB_NAME_, $con);

        $results = array();
        $data = mysql_query("SELECT tax.id_tax, tax.rate, 
                lang.name from ps_tax as tax, 
                ps_tax_lang as lang where 
                tax.id_tax = lang.id_tax 
                and
                lang.id_lang = 1");
        //or die(mysql_error());
        while($row = mysql_fetch_row($data)){
        $results[$row[0]] = new xmlrpcval(array(new xmlrpcval(($row[1]), "string"), new xmlrpcval($row[2], "string")),
            "array");
        }

    return new xmlrpcresp( new xmlrpcval($results, 'struct'));
}

$server = new xmlrpc_server( array( "getTest" => array("function" => "getTest",
                                                         "signature" => array(array($xmlrpcInt))
                                                     ),
                                     "create_category" => array("function" => "create_category",
                                                         "signature" => array(array($xmlrpcInt, $xmlrpcStruct))
                                                     ),
                                     "update_category" => array("function" => "update_category",
                                                          "signature" => array(array($xmlrpcInt, $xmlrpcStruct))
                                                     ),
                                     "update_product" => array("function" => "update_product",
                                                          "signature" => array(array($xmlrpcArray, $xmlrpcStruct))
                                                     ),
                                     "create_product" => array("function" => "create_product",
                                                          "signature" => array(array($xmlrpcArray, $xmlrpcStruct))
                                                     ),
                                     "getTaxes" => array("function" => "getTaxes",
                                                          "signature" => array($xmlrpcStruct)
                                                     ),
                                                 ),false);

$server->functions_parameters_type = 'phpvals';
$server->response_charset_encoding = 'ISO-8859-1';
$server->service();

?>

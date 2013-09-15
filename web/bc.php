<?php
set_time_limit(0);
if (! isset($_POST['detail'])){
	$fields = array('date_order','partner_id','name','amount_total','pricelist_id',);
	$results = $open->purchase_order($fields)->search('state', '=', 'finance_valid');
	foreach ($results as $id => $po){
                $name=$open->res_partner('name')->get($po->partner_id->id)->name;
                $curr=$open->product_pricelist('currency_id')->get($po->pricelist_id->id)->currency_id;
                $curr=$open->res_currency('name')->get($curr->id)->name;
        echo '<tr><td>'.$po->date_order.'</td><td>',$name,'</td><td>',$po->name,'</td>',$po->amount_total,'</td>','<td align="right">',$po->amount_total,$curr,'</td></tr>';
            }
            
        }
 
?>
<form method="post" action="#">
<input type="hidden" name="page" id="page" value="client">
                                   <input type="hidden" name="db" id="db" value="<?php echo $_POST['db']?>"> 
                                   <input type="hidden" name="password" id="password" value="<?php echo $_POST['password']?>"> 
                                   <input type="hidden" name="login" id="login" value="<?php echo $_POST['login']?>">
                                   <table>
                                   </table>
                                   <button name="submit" id="submit">Factures a Valider</button>
                                   <button name="releve" id="releve" type="submit">Relevee</button>
                                   <button name="limit" id="limit" type="submit">Appliquer Limite</button>
                                   <button name="debloquer" id="debloquer" type="debloquer">Debloquer</button>
    </form>

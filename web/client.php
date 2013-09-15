<?php
set_time_limit(0);
if (isset($_POST['releve'])){
	$fields = array('id','name');
	$results = $open->res_partner($fields)->search('ref', '=', $_POST['ref']);
	foreach ($results as $id => $partner){
        echo $partner->name.'<br/>';
        echo "Impayes:<br/>";
        $fields = array('id','invoice','ref','name','partner_id','journal_id','account_id','state','reconcile_id','date_maturity','debit','credit');
		$invoices=$open->account_move_line($fields)->search('partner_id','=',$partner->id);
        foreach ($invoices as $id2 => $invoice)
        {
            $journal_type=$open->account_journal('type')->get($invoice->journal_id->id)->type;
            $account=$open->account_account('type','reconcile')->get($invoice->account_id->id);
            $account_type=$account->type;
            $account_reconcile=$account->reconcile;
            $state=$invoice->state;
            $reconciled=$invoice->reconcile_id;
            if ($invoice->invoice == '') 
            {
                $number='';}
            else
            {
                //$number=$open->account_invoice('number')->get($invoice->invoice->id);
                $number=$invoice->invoice;
            }
            $jt=array('sale','sale_refund');
            $at=array('receivable','payable');
            if (in_array($journal_type,$jt,true) )
            {
                if (in_array($account_type,$at,true) )
                {
                    if($state!='draft')
                    {
                        if ($reconciled=='')
                        {
                            if ($account_reconcile)
                            {
                                echo '<tr><td>'.$number.'</td><td>'.$invoice->ref.'</td><td>',$invoice->date_maturity,'</td>','<td align="right">',($invoice->debit)-($invoice->credit), '</td></tr>';
                            }
                        }
                    }
                }
            }
            
        }
	}

} 
?>
<form method="post" action="#">
<input type="hidden" name="page" id="page" value="client">
                                   <input type="hidden" name="db" id="db" value="<?php echo $_POST['db']?>"> 
                                   <input type="hidden" name="password" id="password" value="<?php echo $_POST['password']?>"> 
                                   <input type="hidden" name="login" id="login" value="<?php echo $_POST['login']?>">
                                   <table>
                                   <tr>
                                        <td>Ref Client
                                        </td>
                                        <td><input type="text" name="ref" id="ref" >
                                        </td>                                        
                                   </tr>
                                   </table>
                                   <button name="submit" id="submit">Factures a Valider</button>
                                   <button name="releve" id="releve" type="submit">Relevee</button>
                                   <button name="limit" id="limit" type="submit">Appliquer Limite</button>
                                   <button name="debloquer" id="debloquer" type="debloquer">Debloquer</button>
    </form>

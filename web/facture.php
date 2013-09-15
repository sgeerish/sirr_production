<?php 
    $fields = array('partner_id', 'state','amount_total');
    $results = $open->account_invoice($fields)->search('number', '=', 'FAA61292');
    foreach ($results as $id => $invoices) {
        print "<h1>" . $id . "</h1>";
        print "<pre>" . $invoices->info() . "</pre>";
        print "<hr>";
    }
?>

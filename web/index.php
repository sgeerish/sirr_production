<title>OpenERP</title>
<?php
include 'openerp_lib/openerplib/openerplib.php';
#include 'openerp_lib/openerplib/openerplib.inc.php';
include 'login.php';
$uid=connect();
if ($uid>0){
    $open = new OpenERP();
    echo '<b/>Bienvenue : ';
    $p = $open->res_users('name')->get($uid);
    print $p->name;
    echo '<br/>';
?>
<table>
<tr>
<td><form method="post" action="#"><input type="hidden" name="page" id="page" value="facture">
                                   <input type="hidden" name="db" id="db" value="<?php echo $_POST['db']?>"> 
                                   <input type="hidden" name="password" id="password" value="<?php echo $_POST['password']?>"> 
                                   <input type="hidden" name="login" id="login" value="<?php echo $_POST['login']?>">
                                   <button name="submit" >Factures a Valider</button>
    </form></td>
<td><form method="post" action="#"><input type="hidden" name="page" id="page" value="bc">
                                   <input type="hidden" name="db" id="db" value="<?php echo $_POST['db']?>"> 
                                   <input type="hidden" name="password" id="password" value="<?php echo $_POST['password']?>"> 
                                   <input type="hidden" name="login" id="login" value="<?php echo $_POST['login']?>">
                                   <button name="submit" >BC a Valider</button>
    </form></td>
<td><form method="post" action="#"><input type="hidden" name="page" id="page" value="client">
                                   <input type="hidden" name="db" id="db" value="<?php echo $_POST['db']?>"> 
                                   <input type="hidden" name="password" id="password" value="<?php echo $_POST['password']?>"> 
                                   <input type="hidden" name="login" id="login" value="<?php echo $_POST['login']?>">
                                   <button name="submit" >Deblocage Client</button>
    </form></td></td>
<td><form method="post" action="#"><input type="hidden" name="page" id="page" value="factures">
                                   <input type="hidden" name="db" id="db" value="<?php echo $_POST['db']?>"> 
                                   <input type="hidden" name="password" id="password" value="<?php echo $_POST['password']?>"> 
                                   <input type="hidden" name="login" id="login" value="<?php echo $_POST['login']?>">
                                   <button name="submit" >Factures a Valider</button>
    </form></td></td>
</tr>
<table>
<?php
if (isset($_POST['page']))
    include $_POST['page'].'.php';
    }
?>
<title>OpenERP Light Client</title>
Welcome to OpenERP Light Client
<br>
<?php
include('xmlrpc.inc');
   $userid=-1;
   $user = $_POST['login'];
   $password = $_POST['password'];
   $dbname = $_POST['db'];
   $server = 'http://localhost:8069/xmlrpc/';
   $sock = new xmlrpc_client($server.'common');

function connect($dbname,$user,$password,$sock,$server) {
   
   $msg = new xmlrpcmsg('login');   
   $msg->addParam(new xmlrpcval($dbname, "string"));
   $msg->addParam(new xmlrpcval($user, "string"));
   $msg->addParam(new xmlrpcval($password, "string"));
   $resp =  $sock->send($msg);
   $val = $resp->value();
   $id = $val->scalarval();
   #$id = $val;

   if($id > 0) {
       return $id;
   }else{
       return -1;
   }
 }

function search($relation,$attribute,$operator,$keys,$dbname,$userid,$password,$sock,$server) {

     $key = array(new xmlrpcval(array(new xmlrpcval($attribute , "string"),
              new xmlrpcval($operator,"string"),
              new xmlrpcval($keys,"string")),"array"),
        );
     $msg = new xmlrpcmsg('execute');
     $msg->addParam(new xmlrpcval($dbname, "string"));
     $msg->addParam(new xmlrpcval($userid, "int"));
     $msg->addParam(new xmlrpcval($password, "string"));
     $msg->addParam(new xmlrpcval($relation, "string"));
     $msg->addParam(new xmlrpcval("read", "string"));
     $msg->addParam(new xmlrpcval($keys, "array"));
     $resp = $sock->send($msg);
     $val = $resp->value();
     $ids = $val->scalarval();
     
    
     return $ids;
}


if ($_POST['db'])
{
    $userid=connect($dbname,$user,$password,$sock,$server) ;
}
else
{
    $userid=-1;
}
   
   
/**
 * $client = xml-rpc handler
 * $relation = name of the relation ex: res.partner
 * $attribute = name of the attribute ex:code
 * $operator = search term operator ex: ilike, =, !=
 * $key=search for
 */
if ($userid>0){ 
echo 'Bienvenu';
echo $uid;
echo search('res.users','id','=',$userid,$dbname,$userid,$password,$sock,$server);
}
else
{

?>

<form method="post" action="index.php">
Base : <select id="db" name="db">
<option>abc_2012</option>
<option>idc_2012_new</option>

</select>
<br/>
Login<input name="login" id="login"/>
<br/>

Password<input type="password" name="password" id="password"/>
<br/>
<button name="submit" id="submit">Valider</button>

</form>
<?php
}
?>
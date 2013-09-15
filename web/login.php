<?php 
if (connect()<=0)
{
?>

<form method="post" action="#">
<table>
<tr>
    <td>Base
    </td>
    <td>
        <select id="db" name="db">
        <option>abc_2012</option>
        <option>idc_2012_new</option>
        </select>
    </td>
</tr>
<tr>
    <td>Login</td>
    <td><input name="login" id="login"/></td>
</tr>
<tr>
    <td>Password</td>
    <td><input type="password" name="password" id="password"/></td>
</tr>
<tr>
<td colspan="2"><button name="submit" id="submit">Valider</button></td>
</tr>
</table>
</form>
<?php
}
?>

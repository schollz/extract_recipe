<?php
if(isset($_POST['submit']) && $_POST['submit']=='Submit'){
     $url=$_POST['fname'];
     echo $url;
echo "<br>";
$command = escapeshellcmd('python extract_recipe.py '.$url);
$output = shell_exec($command);
echo nl2br($output);
     }
else {  
        ?>
<html>
    <head>

    </head>

    <body>
<form method="POST" action="<?=$_SERVER["PHP_SELF"]?>">
        Enter URL of recipe page: <input type="text" name="fname" size=80/>

        <input type="submit" name="submit" value="Submit"/>
</form>
    </body>
</html>
<?php } ?>

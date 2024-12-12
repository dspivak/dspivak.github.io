<?php
$myemail  = "info@catinf.com";

$yourname = $_POST['name'];
$email    = $_POST['email'];
$subject  = $_POST['subject'];
$message  = $_POST['text'];

/* Let's prepare the message for the e-mail */
$message = "The CI contact form has been submitted by:

Name: $yourname
E-mail: $email

$message
";

/* Send the message using mail() function */
mail($myemail, $subject, $message); /* "From: " . email . "\r\n" doesn't work */

/* Redirect visitor to the thank you page */
header('Location: thanks.php');
exit();

?>
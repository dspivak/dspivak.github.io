<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">

<head>
	<title>Blank</title>
	<?php include("head.html"); ?>
</head>

<body>
	<div id="main">
	        <?php include("title.html"); ?>
		<div id="site_content">
		        <?php include("sidebar.html"); ?>
		 
			<div id="content">

				<div class="content_item">
					<h1>Contact us</h1>
					You can email us at <a href="mailto:info@catinf.com">info@catinf.com</a>, or use the form 
					below to send a message.
					<br /> <br />
					 <form action="/contact_action.php" method="post">

    <label for="name">Name:</label>
    <input type="text" id="name" name="name" >
    <br /> <br />

    <label for="email">Email:</label>
    <input type="text" id="email" name="email" >
    <br /> <br />

    <label for="subject">Subject:</label>
    <input type="text" id="subject" name="subject" >
    <br /> <br />

    <label for="text"></label>
    <textarea id="text" name="text" placeholder="Your message" style="height:200px" ></textarea>
<br /> <br />

    <input type="submit" value="Submit">

  </form>
					   
				</div><!-- close content_item -->
					 
			</div><!--close content-->
	
		</div><!--close site_content-->  
	</div><!--close main-->
	<?php include("footer.html"); ?> 
</body>
</html>

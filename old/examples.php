<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">

<head>
	<title>Examples</title>
	<?php include("head.html"); ?>
</head>

<body>
	<div id="main">
	        <?php include("title.html"); ?>
		<div id="site_content">
		        <?php include("sidebar.html"); ?>
		 
			<div id="content">

				<div class="content_item">
					<h1>AQL Examples</h1>  
					
					<ul>
					
					<li>
					<h3><a href="eqs.php">Path Equations</a></h3><p>This example (built in to the IDE with name Employees) defines a schema about employees and departments, with foreign keys taking each employee to the department they work in, each department to the department's secretary, and each employee to their manager.  Two path equations enforce that every secretary works in the department they are the secretary for, and that every employee works in the same department as their manager. </p>
					</li>
					
					<li>
					<h3><a href="denorm.php">Transparent Denormalization</a></h3><p>  This example defines a normalized schema containing information about males and their mothers.  The denormalized schema contains an additional redundant attribute, the name of each male's mother, as well as an equation specifying how the redundant attribute is derived.  When the normalized data is loaded into the denormalized schema, the value of the redundant attribute is automatically computed.  The equation linking the redundant data to the master data will be respected by every AQL operation on the denormalized schema, ensuring that the redundant attribute can never become out of sync.	
					</p>
					</li>

					<li>
					<h3><a href="joinless.php">Transparent Joins</a></h3><p>
					This example defines a source schema about schools, faculty, and departments, and a query to find everyone who works in a school whose largest department is mathematics.  The query does not require any joins; in SQL, the query would require two joins.	</p>
					</li>
					
					<li>
					<h3><a href="quotient.php">Quotients and Transitive Closure</a></h3><p>  This example defines a source schema about people and who likes whom and a target schema with a single entity representing groups connected by liking.  There exists a single schema mapping from the source to the target, and AQL's sigma operation along this mapping computes the connected groups.</p>
					</li>
					
					<li>
					<h3><a href="unitconv.php">High-assurance User-defined Functions</a></h3><p>  This example defines a source schema about American airplanes, which have wing spans in inches, and a target schema about European airplanes, which have wing spans in centimeters.  A user-defined function specifies how to convert inches to centimeters, and a query which does not convert inches to centimeters is rejected.  Although this example uses a relatively simply type conversion, AQL supports user-defined types defined by arbitrary equations.</p>
					</li>
					
					<li>
					<h3><a href="fk.php">Compile-time Foreign Key Checking</a></h3><p>  This example defines a source schema about departments, professors, and students, and a query to find all possible same-department professor-student advising matches.  The target schema relates matches, professors, students, and departments through four foreign keys and an equation enforcing that in every match, the department the professor works in is the same as the department the student is majoring in.  A query that incorrectly populates the target schema is rejected at compile time.</p>
					</li>
					
					<li>
					<h3><a href="jdbc.php">Seamless JDBC Import/Export</a></h3>  <p>This example defines a source schema about employees, and populates an instance on this schema by querying a database using JDBC.  To be self-contained, this example creates a sample in-memory SQL database to import from, but any SQL database accessible over JDBC can be used.</p>
					</li>
					
					</ul>
					
				</div><!-- close content_item -->
					 
			</div><!--close content-->
	
		</div><!--close site_content-->  
	</div><!--close main-->
	<?php include("footer.html"); ?> 
</body>
</html>

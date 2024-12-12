<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">

<head>
	<title>Transparent Joins</title>
	<?php include("head.html"); ?>
</head>

<body>
	<div id="main">
	        <?php include("title.html"); ?>
		<div id="site_content">
		        <?php include("sidebar.html"); ?>
		 
			<div id="content">

				<div class="content_item">
					<h1>Transparent Joins</h1> 
					
					<p>Many data integration tasks require large numbers of joins.  In addition to being a potential perforamnce bottleneck, large joins are difficult to write and debug; a single missing condition in a where clause can cause a query to return an incorrect result.  In AQL, foreign keys can be followed (dereferenced) directly, so that many constuctions that require joins in SQL do not require joins in AQL. 
					</p>
					<p>This example (built in to the IDE with name Joinless) defines a source schema about schools, faculty, and departments, and a query to find everyone who works in a school whose largest department is mathematics.  The query does not require any joins; in SQL, this query would require two joins.	
					</p>
					
					<p>We start by defining a source schema for schools, faculty, and departments, with foreign keys specifying the department and institute of each person, and the biggest department in a school:
					</p>
<p class="contcode">					
<code>typeside Ty = literal { 
	java_types
		String = "java.lang.String"
	java_constants
		String = "return input[0]"
}

schema Schools = literal : Ty {
	entities 
		Person
		School
		Dept
	foreign_keys
		instituteOf : Person -> School 
		deptOf      : Person -> Dept
		biggestDept : School -> Dept
	attributes
		lastName    : Person -> String
		schoolName  : School -> String
		deptName    : Dept   -> String
}
</code>
</p>
<br />
					<p>Here is some sample data, taken from the Boston area:
					</p>
<p class="contcode">					
<code>instance BostonSchools = literal : Schools {
	generators 
		ryan david adam greg gregory jason : Person
		harvard mit : School
		math cs : Dept
	multi_equations 
		lastName -> {ryan Wisnesky, david Spivak, adam Chlipala, greg Morrisett, 
					 gregory Malecha, jason Gross}
		schoolName -> {harvard Harvard, mit MIT}
		deptName -> {math Mathematics, cs CompSci}
		instituteOf -> {ryan harvard, david mit, adam mit, greg harvard, 
			            gregory harvard, jason mit}
		deptOf -> {ryan math, david math, adam cs, greg cs, gregory cs, jason cs}
		biggestDept -> {harvard math, mit cs}
}
</code>
</p>
<img src="examples/joinless2.png" alt="joinless1" width="700" />
<br />

					<p>Our goal is to find all people who work in a school whose biggest department is mathematics.  The target schema contains an entity Person and two attributes:
					</p>
<p class="contcode">					
<code>schema Person = literal : Ty {
	entities 
		Person
	attributes
		lastName   : Person -> String
		schoolName : Person -> String
}</code>
</p>
<br />
					<p>To populate this schema we write a query that iterates over all people, dereferencing foreign keys (using the dot operator) instead of performing joins:   
					</p>
<p class="contcode">					
<code>query BiggestDeptIsMathQuery = literal : Schools -> Person {
	entities
		Person -> {	from p:Person
				 	where p.instituteOf.biggestDept.deptName = Mathematics
				 	return lastName -> p.lastName 
			  			   schoolName -> p.instituteOf.schoolName}
}

instance BiggestDeptIsMathInBoston = eval BiggestDeptIsMathQuery BostonSchools
</code>
</p>
<br />
				<p>The result is displayed in the IDE:
				</p>
				<img src="examples/joinless3.png" alt="joinless2" width="700" />

<p>A screen shot of the entire development is shown below:</p>
<img src="examples/joinless1.png" alt="joinless" width="700" />

				</div><!-- close content_item -->
					 
			</div><!--close content-->
	
		</div><!--close site_content-->  
	</div><!--close main-->
	<?php include("footer.html"); ?> 
</body>
</html>

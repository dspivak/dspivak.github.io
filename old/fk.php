<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">

<head>
	<title>Compile-time Foreign Key Checking</title>
	<?php include("head.html"); ?>
</head>

<body>
	<div id="main">
	        <?php include("title.html"); ?>
		<div id="site_content">
		        <?php include("sidebar.html"); ?>
		 
			<div id="content">

				<div class="content_item">
					<h1>Compile-time Foreign Key Checking</h1> 
					
					<p>Many data integration tasks require creating multiple tables connected by foreign keys.  Typically this process requires disabling foreign key constraints, loading data, and then enabling foreign key constraints, which triggers an expensive runtime check that the foriegn key constraints hold and defers detection of foreign key related bugs until runtime.  In AQL, queries that target schemas containing foreign keys are guaranteed, at compile time, and without accessing any source data, to always materialize target instances with correctly populated foreign keys.  As a result, foreign key related errors are detected much earlier in the ETL process and without costly runtime-checking. 
					</p>
					<p>This example (built in to the IDE with name Foreign Keys) defines a source schema about departments, professors, and students, and a query to find all possible same-department professor-student advising matches.  The target schema relates matches, professors, students, and departments through four foreign keys and an equation enforcing that in every match, the department the professor works in is the same as the department the student is majoring in.  A query that incorrectly populates the target schema is shown to be rejected at compile time.
					</p>
					
					<p>We start by defining a source schema for departments, professors, and students, with foreign keys specifying the department which each professor works in and which each student is majoring in.  For brevity we use an empty typeside.
					</p>
<p class="contcode">					
<code>typeside Ty = empty

schema University = literal : Ty {
	entities
		Professor Student Department
 	foreign_keys
		worksIn    : Professor -> Department
		majoringIn : Student -> Department	
}</code>
</p>
<br />
					<p>Here is some sample data:
					</p>
<p class="contcode">					
<code>instance UniversityOfX = literal : University {
	generators
		Gauss Church Euler : Professor
		Riemann Turing Kleene : Student
		math cs : Department
	multi_equations
		worksIn -> {Gauss math, Church cs, Euler math}
		majoringIn -> {Riemann math, Turing cs, Kleene cs}		
}</code>
</p>
<img src="examples/fk3.png" alt="fk1" width="700" />
<br />

					<p>Our goal is to find all professor-student pairs where the professor and student share the same department.  The target schema contains an additional entitiy for these matches, along with foreign keys to the professor and student involved, and an equation stating the that professor and student share the same department:
					</p>
<p class="contcode">					
<code>
schema AdvisorMatches = literal : Ty {
	imports
		University
	entities
		Match
 	foreign_keys
		studentOf : Match -> Student
		professorOf : Match -> Professor
	path_equations
		studentOf.majoringIn = professorOf.worksIn
}</code>
</p>
<br />
					<p>To populate the target schema we must give one sub query per target entity.  The source tables are copied over directly.  To populate the advisor matches, we iterate over all professors and students, dereferencing foreign keys (using the dot operator) instead of performing joins with Department.  The where clause selects the professors and students which share the same department.  Finally, for each foreign key in the target schema we must specify how it is to be populated.  For example, the majoringIn foreign key takes students to departments; therefore, in the foreign keys clause for majoringIn, we must provide a department (dept), namely (stu.majoringIn), for each student (stu).
					</p>
<p class="contcode">					
<code>query findMatches = literal : University -> AdvisorMatches {
 entities
	Department -> {from dept:Department}
		
	Professor -> {from prof:Professor}

	Student -> {from stu:Student}

	Match -> {from p:Professor s:Student 
		      where p.worksIn = s.majoringIn} 

foreign_keys		 	   

	majoringIn -> {dept -> stu.majoringIn}
	
	worksIn -> {dept -> prof.worksIn}
	
	professorOf -> {prof -> p}
	
	studentOf -> {stu -> s}
}

instance MatchesForUnivX = eval findMatches UniversityOfX</code>
</p>
<br />
				<p>The result is displayed in the IDE.  Note that the generated IDs for the matches contain the provenance, or lineage, of how the match was formed.   
				</p>
				<img src="examples/fk2.png" alt="fk2" width="700" />
				
				<p>If the sub query for Match does not correctly populate the target table, say because of a typo:   
				</p>
<p class="contcode">					
<code>Match -> {from p:Professor s:Student 
		where p.worksIn = p.worksIn} 
</code>	
</p>
<br />
				<p>The IDE rejects the query at compile time:
				</p>
<p class="contcode">					
<code>Error in query findMatches: 
	Target equation 
		v.studentOf.majoringIn = v.professorOf.worksIn 
	not respected: transforms to 
		s.majoringIn = p.worksIn
	which is not provable in the sub-query for Match.
</code>
</p>
<br />
				
<p>A screen shot of the entire development is shown below:</p>
<img src="examples/fk1.png" alt="fk3" width="700" />

				</div><!-- close content_item -->
					 
			</div><!--close content-->
	
		</div><!--close site_content-->  
	</div><!--close main-->
	<?php include("footer.html"); ?> 
</body>
</html>

# Intro 
This software (**C**alculator f**O**r **M**arine **I**ndicators and **C**haracteristics - **COMIC**) was developed into the work package 
[WP6 Assessmento of Good Environmental Status for the oceans and seas] (http://www.melodiesproject.eu/node/35), 
in project [MELODIES - http://www.melodiesproject.eu] (http://www.melodiesproject.eu) . 

**The MELODIES project - Maximizing the Exploitation of Linked Open Data In Enterprose and Science** : 
this project aims to demonstrate the business and scientific benefits of releasing data openly through real applications .

**WP6 Assessment of Good Environmental Status for the oceans and seas** : a new service was developed 
within the MELODIES project, for the assessment of GES (Good Environmental Status) and support its achievement 
by 2020 as defined in [Marine Strategy Framework Directive - DIRECTIVE 2008/56/EC OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL] (http://ec.europa.eu/environment/marine/eu-coast-and-marine-policy/marine-strategy-framework-directive/index_en.htm)


# COMIC

This software aims to compute *GES characteristics and indicators* from *multi-year Earth Observation and Model datasets*, available as [open data](https://open-data.europa.eu/en/data) 

The initial design took into consideration issues related to the huge volume of available inputs, 
hence the performance requirements, due to such kind of applications, 
and the efficiency in computation and data access, due to the growing relevance of the [sustainability](http://ec.europa.eu/environment/eussd/) issue. 
The development is based as much as possible on criteria for software and technology **reusability**. 


## Features

The following list is going to be updated during the development.

Functional :

* possible to select the working area in terms of lon/lat boxes
* possible output : map or time-series
* possible to perform one or more of the following computation 
	* average over spatial vertical dimension 
	* average over time 
	* average over spatial horizontal dimension
	* climatological averaging

Technical :

* possible to provide the input by means of a stream of filename through the standard input (stdio) at execution time
* possible to implement a Map/Reduce workflow
* adopted standard : 
	* output in file format NetCDF4, convention CF-1.6
* possible to output benchmarking information
* possible to activate memory efficient working mode


## Development environment

List of prerequisites for this software execution :

* NetCDF library - test done with version 4.4.1
* Python - test done with version 2.7.12
* numpy - test done with version 1.11.1
* netcdf4-python - test done with version 1.2.4
* seawater - test done with version 3.3.4

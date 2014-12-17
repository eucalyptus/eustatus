eustatus
========

A set of utilities for collecting and displaying operational information from multiple Eucalyptus clouds.


Checkclouds
-----------

A set of utilities for collecting and displaying operational information from multiple Eucalyptus clouds.

installation instructions
-------------------------

1. Copy checkclouds.php to your PHP and jQuery capable web server 
   cp checkclouds.php  /var/www/html # or /var/www
2. Install minimised jQuery 1.8.19 libraries to /jQuery in your web server.
   N.B. if you use a different version you may have to customise the included web pages.
3. Install eutester from Eucalyptus github.
3. Configure your crontab to run eutester according to the crontab example
4. Visit checkclouds.php in your web browser 


Cloud usage history
-------------------

installation
------------

Cloud history is an set of python scripts that query EC2 api periodically
and store the data to postgreSQL database for further analysis of past of the cloud

Setup
-----

Expects RHEL/CENTOS6 [tested on rhel6.5 64b] and Eucalyptus 4.0.1

Create keypair for use with history instance

Modify the vars/euca-dw.yml to match your environment

Source your clouds credentials

Launch the playbook with command
ansible-playbook -vvv --private-key=mykey.private cloudhistory-ec2.yml

Use reemon for read only access to history db
eemon to write access to historydb

Playbook will create security group and allow the access to ports 80,22,8443,ping by default

Use
---

Access the data with browser using http://instanceaddress
Or query the DB from outside with readonly user reemon

Licensing 
--------- 
The code included was written by a subcontractor working for Nokia
Siemens Networks and Nokia Solutions and Networks.

The majority of the code is released by Nokia Siemens Networks under
the Apache license - please see APSL-2.0.txt included in the source
distribution.  For convenience certain small or trivial files
(e.g. the crontab) are released to the public domain (or CC0 in
jurisdictions where the public domain is not applicable - please see
the file CC0-1.0.txt in the distribution).

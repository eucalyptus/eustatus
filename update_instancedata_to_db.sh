#/bin/sh
#
#  Copyright Nokia Siemens Networks 2013, Authored by Teemu Jalonen
#

if [ $# -lt 1 ]
then
        echo "Usage : update_instancedata_to_db.sh <cloudname>"
        exit 1
else
        export http_proxy=
        CLOUDNAME=$1
	source /etc/eutester/.euca_$CLOUDNAME\_admin/eucarc
	euca-describe-instances verbose --debug 2> /home_local/histuser/cloudhistory/euca-describe-instances_verbose_$CLOUDNAME\.xml
	tidy -xml -i -q  -w 0 -o /home_local/histuser/cloudhistory/$CLOUDNAME\_tidy_instances.xml < /home_local/histuser/cloudhistory/euca-describe-instances_verbose_$CLOUDNAME\.xml
	/home_local/histuser/cloudhistory/readinsertinstances.py -n $CLOUDNAME\history -p histpass -x /home_local/histuser/cloudhistory/$CLOUDNAME\_tidy_instances.xml
fi

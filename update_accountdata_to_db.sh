#/bin/sh
#
#  Copyright Nokia Siemens Networks 2013, Authored by Teemu Jalonen
#

if [ $# -lt 1 ]
then
        echo "Usage : update_accountdata_to_db.sh <cloudname>"
        exit 1
else
        export http_proxy=
        CLOUDNAME=$1
        source /home_local/histuser/cloudhistory/.euca_$CLOUDNAME\_admin/eucarc
        euare-accountlist --debug 2> /home_local/histuser/cloudhistory/euare-accountlist_$CLOUDNAME\.xml
        tidy -xml -i -q -w 0 -o /home_local/histuser/cloudhistory/$CLOUDNAME\_tidy_accountlist.xml < /home_local/histuser/cloudhistory/euare-accountlist_$CLOUDNAME\.xml
        /home_local/histuser/cloudhistory/readinsertaccounts.py -n $CLOUDNAME\history -p histpasswd -x /home_local/histuser/cloudhistory/$CLOUDNAME\_tidy_accountlist.xml
fi

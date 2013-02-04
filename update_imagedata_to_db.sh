#/bin/sh
#
#  Copyright Nokia Siemens Networks 2013, Authored by Teemu Jalonen
#

if [ $# -lt 1 ]
then
        echo "Usage : update_imagedata_to_db.sh <cloudname>"
        exit 1
else
        export http_proxy=
        CLOUDNAME=$1
        source /home_local/histuser/cloudhistory/.euca_$CLOUDNAME\_admin/eucarc
        euca-describe-images --debug 2> /home_local/histuser/cloudhistory/euca-describe-images_$CLOUDNAME\.xml
        tidy -xml -i -q -w 0 -o /home_local/histuser/cloudhistory/$CLOUDNAME\_tidy_images.xml < /home_local/histuser/cloudhistory/euca-describe-images_$CLOUDNAME\.xml
        sed -i 1i"<root>" /home_local/histuser/cloudhistory/$CLOUDNAME\_tidy_images.xml
        echo "</root>" >> /home_local/histuser/cloudhistory/$CLOUDNAME\_tidy_images.xml
        /home_local/histuser/cloudhistory/readinsertimages.py -n $CLOUDNAME\history -p histpass -x /home_local/histuser/cloudhistory/$CLOUDNAME\_tidy_images.xml
fi

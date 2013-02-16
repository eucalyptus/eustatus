#/bin/sh
#
#  Copyright 2013 Nokia Siemens Networks, Authored by Teemu Jalonen
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
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

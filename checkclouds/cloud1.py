#!/usr/bin/env python
#
# Description: This script runs one m1.small instance on an eucalyptus cloud defined by the eucarc file in the credentials path. 
# This test checks instance startup, userdata, ebs functionality and speed and snapshots.
# This script is a modified version of the eutester instancechecks.py script by Vic Iglesias at Eucalyptus
# Script modifications done by Ilpo Latvala 

import unittest, os
from eucaops import Eucaops

class MyFirstTest(unittest.TestCase):

    def setUp(self):
        self.tester = Eucaops(credpath="/etc/eutester/.euca_cloud1_user/")
        self.keypair = self.tester.add_keypair()
        self.group = self.tester.add_group()
        self.tester.authorize_group(self.group)
        self.tester.authorize_group(self.group, port=-1, protocol="icmp")
        self.reservation = None

    def testInstance(self):
	image = self.tester.get_emi("emi-5F87351C")
        ### 1) Run an instance
        try:
            self.reservation = self.tester.run_instance(image, self.keypair.name, self.group.name, user_data="echo 'userdata is working' > /tmp/userdata.txt",type="m1.large",min=1,max=1)
        except Exception, e:
            self.fail("Caught an exception when running the instance: " + str(e))
        for instance in self.reservation.instances:
            ### 2) Ping the instance
            ping_result = self.tester.ping(instance.public_dns_name)
            self.assertTrue(ping_result, "Ping to instance failed")
            ### 3) Run command on instance
            uname_result = instance.sys("uname")
            self.assertNotEqual(len(uname_result), 0, "uname failed")
            ### 4) Check userdata
	    self.tester.sleep(10)
            userdata_result = instance.sys("cat /tmp/userdata.txt")
            self.assertNotEqual(len(userdata_result), 0, "userdata failed")

            ### Ensure we know what device are on the instance before the attachment of a volume
            before_attach = instance.sys("ls -1 /dev/ | grep vd")

            ## Create the volume
            volume = self.tester.create_volume(self.tester.ec2.get_all_zones()[0].name, size=2)

            ### Attach the volume (need to write a routine to validate the attachment)
            volume.attach(instance.id, "/dev/vdb")

            self.tester.sleep(20)

            ### Check what devices are found after the attachment
            after_attach = instance.sys("ls -1 /dev/ | grep vd")

            ### Use the eutester diff functionality to find the newly attached device
            new_devices = self.tester.diff(after_attach, before_attach)
            attached_block_dev = new_devices[0].strip()

            ### Make a file system on the volume and mount it
            instance.sys("mkfs.ext4 -F /dev/" + attached_block_dev )
            instance.sys("mkdir /mnt/device" )
            instance.sys("mount /dev/" +  attached_block_dev  + " /mnt/device")

            ### Test speed of EBS
            instance.sys("echo '[Info] Performing WRITE test'")
            instance.sys("dd if=/dev/zero of=/mnt/device/speedtest.tmp bs=1M count=1000 conv=fdatasync 2>&1 | grep MB")
            instance.sys("echo '[Info] Finished WRITE test'")
            instance.sys("echo '[Info] Performing READ test'")
            instance.sys("dd if=/mnt/device/speedtest.tmp of=/dev/zero 2>&1 | grep MB")
            instance.sys("echo '[Info] Finished READ test'")
            instance.sys("echo '[Info] Removing tmp file'")
            instance.sys("rm -f /mnt/device/speedtest.tmp")

            ### Unmount the volume
            if instance.sys("umount /mnt/device") != []:
               self.tester.fail("Failure unmounting volume")

            ### Make a snapshot of the volume
            snapshot = self.tester.create_snapshot(volume.id)
            ### Delete the snapshot
            self.tester.delete_snapshot(snapshot)

            ### TEARDOWN INSTANCES, VOLUMES GROUP, KEYPAIR, AND ADDRESSES

            self.tester.detach_volume(volume)
            self.tester.delete_volume(volume)
            instance.terminate()
            self.tester.sleep(20)


    def tearDown(self):
        if self.reservation is not None:
            self.tester.terminate_instances(self.reservation)
        self.tester.delete_keypair(self.keypair)
        self.tester.local("rm " + self.keypair.name + ".pem")
        self.tester.delete_group(self.group)

if __name__ == '__main__':
    os.system("timeout 60 euca-describe-availability-zones verbose -a adminaccesskey -s adminsecretkey -U http://cloud1.net:8773/services/Eucalyptus |grep m1.small| awk '{print $4 $5 $6}'")
    os.system("AC=`timeout 60 /usr/bin/euca-describe-addresses -a adminaccesskey -s adminsecretkey -U http://cloud1.net:8773/services/Eucalyptus`;X=`echo $AC | grep -o nobody | wc -l`;Y=`echo $AC | grep -o ADDRESS | wc -l`;echo -ne $X;echo -ne '/';echo $Y")
    os.system("timeout 20 ssh cloud1.net euca_conf --version")
    unittest.main()


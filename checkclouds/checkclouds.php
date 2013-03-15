<?php
/*
#
#  php script to make a webpage of eutester output for various clouds 
#
#
#  Copyright Nokia Siemens Networks 2013, Authored by Ilpo Latvala
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
*/
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
<head>
<title> Cloud Status </title>
<meta http-equiv="refresh" content="900" >
<STYLE type="text/css">
   b.arrow {float: right}
</STYLE>
</head>
<body>

<table width="100%" style="border:none;">
	<tr>
		<td><h1>Cloud Status</h1></td>
                <td width="50%" align="right">
		<ul id="tips">
		<li>Note 1</li>
		<li>Note 2</li>
		<li>Note 3</li>
		</ul>
		</td>
	</tr>
</table>

<style type="text/css">
h1 {color:black; text-decoration: none; font-size: 40px; font-family: Arial; }
h3.cloud {font-size:16px;}
p {color:black;}
p.infotext {color:white; font-size:18px; text-decoration: none;}
#tips, #tips li{
	margin:0;
	padding:0;
	list-style:none;
	}
#tips{
	width:50%;
	font-size:16px;
	line-height:120%;
	font-family: Arial;
	}
#tips li{
	padding:20px;
	background:#ffcc33;
	display:none; /* hide the items at first only to display one with javascript */
	}
td { vertical-align:top; align:center; height:52px;}
button { height:42px; }
img { border-style: none; }
</style>

<link href="../jQuery/css/ui-lightness/jquery-ui-1.8.19.custom.css" rel="stylesheet" type="text/css"/>
<script src="../jQuery/jquery.min.js"></script>
<script src="../jQuery/jquery-ui.min.js"></script>

<script>
$(document).ready(function() {
    $("#tabs").tabs();
    $("#accordion-1").accordion({ active: -1, autoHeight : false, collapsible: true });
    $("#tabs").tabs({ selected: 1 });
    $("#accordion-2").accordion({ active: -1, autoHeight : false, collapsible: true });
    $("#tabs").tabs({ selected: 0 });
    $("#accordion-3").accordion({ active: -1, autoHeight : false, collapsible: true });
    $("#tabs").tabs({ selected: 0 });
  });
</script>

<script type="text/javascript">
this.randomtip = function(){
	var length = $("#tips li").length;
	var ran = Math.floor(Math.random()*length) + 1;
	$("#tips li:nth-child(" + ran + ")").show();
};

$(document).ready(function(){	
	randomtip();
});

$(function() {
   //capture the click on the a tag
   $("#accordion-1 b").click(function() {
      window.location = $(this).attr('arrow');
      return false;
   });
   $("#accordion-2 b").click(function() {
      window.location = $(this).attr('arrow');
      return false;
   });
   $("#accordion-3 b").click(function() {
      window.location = $(this).attr('arrow');
      return false;
   });
});

</script>


<?php //list here all eutester output files
ob_start();

$clouds[1] = array("/var/www/html/git/cloud1.txt", "/var/www/html/git/cloud2.txt", "/var/www/html/git/cloud3.txt" );
$clouds[2] = array("/var/www/html/git/cloud4.txt" );
$clouds[3] = array("/var/www/html/git/cloud5.txt" );

echo "<div id=\"tabs\" style=\"background: #555; \">";
echo "<ul>";
echo "<li><a href=\"#tabs-1\">Production</a></li>";
echo "<li><a href=\"#tabs-2\">Pre-Production</a></li>";
echo "<li><a href=\"#tabs-3\">QA</a></li>";
echo "</ul>\n";

for ( $count = 1; $count <= 3; $count += 1) {
echo "<div id=\"tabs-" . $count . "\">";
echo "<div id=\"accordion-" . $count . "\">";

//print each eutester output file
$ccounter = 0;
foreach($clouds[$count] as $cloud)
{
$cloud_file = file_get_contents($cloud);
$pos = strpos($cloud_file, "\n");
$pos2 = strpos($cloud_file, "\n", $pos);
$usagenum = substr($cloud_file, 0, $pos);
$usagenum2 = substr($cloud_file, $pos, $pos2);
$usagearr = explode("/", $usagenum );
$usagearr2 = explode("/", $usagenum2 );
$eucaline = "";
$eucaver = "";
preg_match("/eucalyptus [a-z0-9 :.-]+/i", $cloud_file, $eucaline);
preg_match("/[0-9.]+/", $eucaline[0], $eucaver);
if ($eucaver[0]<>"") { $eucaver[0] = "(v." . $eucaver[0] . ") "; }

$usage="";
if (ereg("([0-9]{4})/([0-9]{4})", $usagenum) && ereg("([0-9])/([0-9])", $usagenum2)) {
      $usage=" Available cores: <font color=\"blue\">" . intval($usagearr[0]) . "/" . intval($usagearr[1]) . "</font> Available IPs: <font color=\"blue\">" . intval($usagearr2[0]) . "/" . intval($usagearr2[1]) . "</font> Cloud usage: <font color=\"blue\">" . round(100 - intval($usagearr[0])*100/intval($usagearr[1])) . "% </font>" ;
}
// Check for userdata
if(stristr($cloud_file,"userdata is working") == TRUE) {
        $userdata="green";
}
else {
        $userdata="red";
}
// Check for Volumes
if(stristr($cloud_file,"(1.0 GB) copied") == TRUE) {
        $volumecheck="green";
}
else {
        $volumecheck="red";
}

// Check for instance startup
if(stristr($cloud_file,"Linux") == TRUE) {
        $startupcheck="green";
}
else {
        $startupcheck="red";
}

echo "<h3 class=\"cloud\"><a href=\"#\">" . strtoupper(basename($cloud, ".txt").PHP_EOL);
echo $eucaver[0];
echo "<font color=\"" . $startupcheck . "\" title=\"instance startup\">&#9632;</font><font color=\"" . $userdata . "\" title=\"userdata\">&#9632;</font><font color=\"" . $volumecheck . "\" title=\"volume check\">&#9632;</font>" . "     " . $usage . date ("H:i:s", filemtime($cloud)) . " EET" . "<b class=\"arrow\" arrow=\"cloudinfo.php?cname=" . basename($cloud, ".txt").PHP_EOL . "\">Additional info &#9658;</b>";
echo "</a></h3>";
echo "<div>";
echo "Last check: " . date ("F d Y H:i:s.", filemtime($cloud)) . "<br>";
echo "<p style=\"font-size:8pt\">";
echo nl2br($cloud_file) . "</p>";
echo "</div>";
}
echo "</div>";
echo "</div>";
}
echo "</div>";
ob_get_content();
?>

</body>
</html>

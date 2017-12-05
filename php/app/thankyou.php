<?php
	require_once("include/config.php");
	require_once("include/salesforce.inc");

	if ($_SERVER['REQUEST_METHOD'] === 'POST') {
		$SFData = json_decode(file_get_contents(__DIR__ . "/SF.json"), true);
	
		$instance_url = $SFData["instance_url"];
		$access_token = $SFData["access_token"];
		$refresh_token = $SFData["refresh_token"];

		$lead = getSFQueryResult("SELECT Id FROM Lead WHERE email = '$_POST[email]'")["records"][0];
		$updatedLeadFields = array("Splashtop_Id__c" => $_POST['Splashtop_Id__c']);
		updateSFObject("Lead", $lead['Id'], $updatedLeadFields);

		header("Location: /thankyou.php");
		die();
	}
?>
<html>

<head>
<link rel="icon" href="http://adsrental.com/rasbpi_icon.ico" />
<link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
<script
	src="https://code.jquery.com/jquery-3.2.1.min.js"
	integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4="
	crossorigin="anonymous"></script>
<title>Thank you for joining us</title>
<style>
	.image_thumbnail {
		display: none;
		position: absolute;
		border: 2px solid black;
		margin-top: -200px;
	}

	.image_hover {
		border-bottom: 1px dashed black;
		cursor: pointer;
		color: #337ab7;
	}
</style>
</head>

<body>
	<div class="jumbotron">
		<div class="container">
			<h1 class="display-3">Thank You for Registering!</h1>
			<p>You Have Been Pre-approved!</p>
		</div>
	</div>
	<div class="container">

		<h3>Thank you for registering! Follow these simple steps to collect your initial payment</h3>
		<ol style="font-size:150%;">
			<li>
				Please follow the download link below to install Spashtop on your computer.
				<a href="https://my.splashtop.com/team_deployment/download/JLXKK3TR3ZLP" target="_blank">https://my.splashtop.com/team_deployment/download/JLXKK3TR3ZLP</a>
			</li>
			<li>
				Please input the
				<span class="image_hover">Splashtop ID (hover to see how to find it)</span>
				<img class="image_thumbnail" src="static/images/splashtop.png" />
				assigned to your computer in the box below. Follow the screen shots above to locate it on your computer.
			</li>
			<li>
				Tell your recruiter that you have downloaded Splashtop and are ready for one of our agents to connect to your computer. Our agents are online between 7 am - 8 pm PST.
			</li>
			<li>
				An agents will login and verify your FB account meets our requirements. This is the only time we will access your computer. Once Verified, you may remove the Splashtop program from your device.
			</li>
		</ol>
	</div>
	<div class="container">
		<?php if ($_GET["email"]) { ?>
			<div class="container">
				<form action="" method="POST">
					<input type="hidden" name="email" value="<?php echo $_GET["email"] ?>" />
					<input type="text" name="Splashtop_Id__c" value="" required placeholder="Splashtop ID" />
					<button>Submit</button>
				</form>
			</div>
		<?php } else { ?>
			<h3>Thank you! Our agent will contact you shortly.</h3>
		<?php } ?>
	</div>
	<footer class="container">
		<p>© Adsrental 2017</p>
	</footer>
</body>

<script>
	$(function () {
		$(".image_hover").hover(function () {
			$('.image_thumbnail').show();
		}, function () {
			$('.image_thumbnail').hide();
		});
	});
</script>

</html>
<?php
  ini_set("error_reporting","E_ALL & ~E_NOTICE"); 
  session_start();

  $myfile = fopen("/alldata/bblab_site/logs/hla_debugging.log", "a");
  fwrite($myfile, "----\n");
  fwrite($myfile, date("h:i:sa Y-m-d") . " Opening HLA debugging log.\n");
  $session_string_dump = print_r($_SESSION, true);
  fwrite($myfile, "session: " . $_SESSION . "\n");
  fwrite($myfile, "session results: " . $_SESSION["results"] . "\n");
  fclose($myfile);

  //hmmm  
  if ($_SESSION["results"]) {
    unlink($_SESSION["results"]);
    unlink($_SESSION["details"]);
    unlink($_SESSION["tech_errors"]);
    unlink($_SESSION["errors"]);
    //posix_kill($_SESSION["pid"], 15); // SIGTERM, I hope.
  }
    
  if ($_SESSION["updates"]) {
    unlink($_SESSION["updates"]);
  }

  $ruby = "/root/.rbenv/shims/ruby";
  $script = dirname(__FILE__) . "/hla-easy.rb";
  $_SESSION["results"] = dirname(__FILE__) . tempnam("/tmp", "");
  $_SESSION["details"] = dirname(__FILE__) . tempnam("/tmp", "");
  $_SESSION["tech_errors"] = dirname(__FILE__) . tempnam("/tmp", "");
  $_SESSION["errors"] = dirname(__FILE__) . tempnam("/tmp", "");

  $myfile = fopen("/alldata/bblab_site/logs/hla_debugging.log", "a");
  $session_string_dump = print_r($_SESSION, true);
  fwrite($myfile, "session (after setting some variables): " . $_SESSION . "\n");
  fwrite($myfile, "session results: " . $_SESSION["results"] . "\n");
  fwrite($myfile, "session details: " . $_SESSION["details"] . "\n");
  fwrite($myfile, "session tech_errors: " . $_SESSION["tech_errors"] . "\n");
  fwrite($myfile, "session errors: " . $_SESSION["errors"] . "\n");
  fclose($myfile);

  $letter = $_POST["letter"];
  $threshold = $_POST["threshold"];
  $fasta_text = $_POST["fasta_text"];

  $myfile = fopen("/alldata/bblab_site/logs/hla_debugging.log", "a");
  fwrite($myfile, "Parameters:\n");
  fwrite($myfile, "letter: " . $letter . "\n");
  fwrite($myfile, "threshold: " . $threshold . "\n");
  fwrite($myfile, "fasta_text: " . $fasta_text . "\n");
  fclose($myfile);
  
  
  $descriptors = array (
    0 => array("pipe", "r"),
    1 => array("file", $_SESSION["results"], "a"),
    2 => array("file", $_SESSION["tech_errors"], "a"),
    7 => array("file", $_SESSION["errors"], "a"),
    8 => array("file", $_SESSION["details"], "a")
  );

  
  
  if ($threshold >= 0) {
    $cmd = sprintf("echo \"%s\" | %s %s -t %s %s &", $fasta_text, $ruby,
      $script, $threshold, $letter); 
  } else {
    $cmd = sprintf("echo \"%s\" | %s %s --threshold=\"-1\" %s &", $fasta_text, $ruby,
      $script, $letter); 
  }

  $myfile = fopen("/alldata/bblab_site/logs/hla_debugging.log", "a");
  fwrite($myfile, "Invoking Ruby.\n");
  fwrite($myfile, "Ruby executable: " . $ruby . "\n");
  fwrite($myfile, "script: " . $script . "\n");
  fwrite($myfile, "command: " . $cmd . "\n");
  fclose($myfile);
  
  $process = proc_open($cmd, $descriptors, $pipes);

  $myfile = fopen("/alldata/bblab_site/logs/hla_debugging.log", "a");
  fwrite($myfile, "process: " . $process . "\n");
  fclose($myfile);

  $pstatus = proc_get_status($process);

  $myfile = fopen("/alldata/bblab_site/logs/hla_debugging.log", "a");
  fwrite($myfile, "pstatus: " . $pstatus . "\n");
  fclose($myfile);
  
  $_SESSION["pid"] = $pstatus["pid"];

  $myfile = fopen("/alldata/bblab_site/logs/hla_debugging.log", "a");
  fwrite($myfile, "pid (?): " . $pstatus["pid"] . "\n");
  fclose($myfile);

  fclose($pipes[0]);
  proc_close($process);

  $myfile = fopen("/alldata/bblab_site/logs/hla_debugging.log", "a");
  fwrite($myfile, "Done with Ruby.\n");
  fclose($myfile);
  
  $resfile =  "/django/tools/hla_class/tmp/" . array_pop(explode("/", $_SESSION["results"]));
  $detfile =  "/django/tools/hla_class/tmp/" . array_pop(explode("/", $_SESSION["details"]));
  $techerrfile = "/django/tools/hla_class/tmp/" . array_pop(explode("/", $_SESSION["tech_errors"]));
  $errfile = "/django/tools/hla_class/tmp/" . array_pop(explode("/", $_SESSION["errors"]));
  printf("%s\n%s\n%s\n%s", $resfile, $detfile, $techerrfile, $errfile);
?>

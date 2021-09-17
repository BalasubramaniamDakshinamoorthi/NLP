#!/usr/bin/perl
#

$previous = "";

while(<>) {

	@line = split('\^');

	#print("line[0] = $line[0]\n");

	#print("previous = $previous\n");

	if ($line[0] eq $previous) {

		#print("Found duplicate...\n")

		next;
	}

	print;

	$previous = $line[0];
}


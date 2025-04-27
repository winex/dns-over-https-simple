#!/usr/bin/env python3

# see: https://blog.kiserai.net/crafting-a-dns-over-https-get-request-manually

import sys
import dns.message
import requests
import base64


DEFAULT_DOH_URL = "https://cloudflare-dns.com/dns-query"

def doh_query(host, url=DEFAULT_DOH_URL):
	req_raw = dns.message.make_query(host, 'A', id=0).to_wire()
	req_str = base64.urlsafe_b64encode(req_raw).decode('utf-8').rstrip('=')
	resp = requests.get(url + "?dns=" + req_str)
	resp.raise_for_status()
	return dns.message.from_wire(resp.content)


def print_usage(argv):
	print(
		f"Usage: {argv[0]} [OPTIONS] domain-name.tld[.]\n"
		"Options:\n"
		"	-h|--help		print this help\n"
		"	-?|--????		some other option\n"
	, file=sys.stderr)


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print_usage(sys.argv)
		sys.exit(1)
	if sys.argv[1] == "-h" or sys.argv[1] == "--help":
		print_usage(sys.argv)
		sys.exit(0)

	for arg in sys.argv[1:]:
		result = "ERROR"
		try:
			result = doh_query(arg)
		except Exception as e:
			print(e, file=sys.stderr)
			pass
		print(result)


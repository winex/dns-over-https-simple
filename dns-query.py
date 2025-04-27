#!/usr/bin/env python3

# see: https://blog.kiserai.net/crafting-a-dns-over-https-get-request-manually

import sys, os
import dns.message
import dns.query
import requests
import base64
import json
import urllib


DEBUG = False
#DEBUG = True
VERBOSE = False

DEFAULT_TIMEOUT = 3
DEFAULT_DOH_URL = "https://cloudflare-dns.com/dns-query"
# ok, dns.query.[proto]() needs vars, not urls
DEFAULT_DNS = ("127.0.0.1", 53)

# WARN: dont touch manually
_IS_CGI = False


def doh_query(host, url=DEFAULT_DOH_URL):
	req_raw = dns.message.make_query(host, 'A', id=0).to_wire()
	req_str = base64.urlsafe_b64encode(req_raw).decode('utf-8').rstrip('=')
	resp = requests.get(url + "?dns=" + req_str)
	resp.raise_for_status()
	return dns.message.from_wire(resp.content)

def dns_query_dns(data, addr=DEFAULT_DNS, timeout=DEFAULT_TIMEOUT):
	req_b64 = base64.urlsafe_b64decode(data + '=' * (-len(data) % 4))
	req_raw = dns.message.from_wire(req_b64)
	# NOTE: there is also dns.query.tls() ;)
	resp = dns.query.udp(req_raw, where=addr[0], port=addr[1], timeout=timeout)
	if not _IS_CGI and VERBOSE:
		print(resp, file=sys.stderr)
	return resp.to_wire()

def dns_query_name(host, addr=DEFAULT_DNS, timeout=DEFAULT_TIMEOUT):
	# TODO: check validity of host?
	req_raw = dns.message.make_query(host, 'A', id=0)
	resp = dns.query.udp(req_raw, where=addr[0], port=addr[1], timeout=timeout)
	if not _IS_CGI and VERBOSE:
		print(resp, file=sys.stderr)
	return resp.to_wire()


def serve_cgi(env):
	# NOTE: it is set here...
	_IS_CGI = True

	path  = env.get("PATH_INFO")
	query = env.get("QUERY_STRING")
	# why the fuck we do JSON?!
	#environ = json.dumps(str(env), indent=2)
	environ = "\n".join([f"{k}={env[k]}" for k in sorted(env.keys())])
	# TODO: we need select() or poll() for timeout, so sad... :(
	#content = sys.stdin.read(timeout=5)
	content = sys.stdin.read()

	if DEBUG:
		content_safe = content.encode("utf-8")
		# spam error_log with this:
		#print(f'request {path}', file=sys.stderr)
		print(f"Content-type: text/html", end="\r\n")
		print(end="\r\n")
		print(
			"<h1>Python3 CGI debug mode, not doing any actual requests!</h1>\n"
			f"<h4>os.environ:</h4><pre>{environ}</pre>\n"
			f"<h4>path:</h4><pre>'{path}'</pre>\n"
			f"<h4>query:</h4><pre>'{query}'</pre>\n"
			f"<h4>stdin:</h4><pre>{content_safe}</pre>\n"
		)
		#return

	# DEBUG: try this here
	#query = "dns=AAABAAABAAAAAAAABmdvb2dsZQJydQAAAQAB&name=google.ru"
	#query = "dns=AAABAAABAAAAAAAABmdpdGh1YgNjb20AAAEAAQ&name=github.com"

	# make requests
	q = urllib.parse.parse_qs(query)
	# TODO: idk if appending dns wire data is acceptable...
	ret = b""
	try:
		for v in q["dns"]:
			ret += dns_query_dns(v)
	except KeyError:
		pass
	try:
		for v in q["name"]:
			ret += dns_query_name(v)
	except KeyError:
		pass

	# finally, send response
	if len(ret) <= 0:
		return
	header = f"Content-type: application/dns-message\r\n"
	if DEBUG:
		print(f"<h4>response:</h4><pre>{header}{str(ret)}</pre>")
		return
	sys.stdout.buffer.write(header.encode("utf-8") + b"\r\n")
	sys.stdout.buffer.write(ret)


def print_usage(argv):
	print(
		f"Usage: {argv[0]} [OPTIONS]... domain-name.tld[.] ...\n"
		"Options:\n"
		"	-h|--help		print this help\n"
		"	-?|--????		some other option\n"
	, file=sys.stderr)


if __name__ == "__main__":
	# NOTE: it seems we can't pass any arguments to CGI scripts, at least in Apache
	# it breaks command-line with no args message :(. we can check TTY, though
	if len(sys.argv) < 2 \
	or sys.argv[1] == "-c" or sys.argv[1] == "--cgi":
		serve_cgi(os.environ.copy())
		sys.exit(0)
	if sys.argv[1] == "-h" or sys.argv[1] == "--help":
		print_usage(sys.argv)
		sys.exit(0)

	for arg in sys.argv[1:]:
		result = "ERROR"

		# sorry for this
		_func = dns_query_name
		if arg.startswith("dns="):
			_func = dns_query_dns
			arg = arg[3:]

		try:
			result = _func(arg)
		except Exception as e:
			print(e, file=sys.stderr)
			#raise
			pass
		print(result)


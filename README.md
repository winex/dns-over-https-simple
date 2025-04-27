# DoH (dns-over-https) python3 utillites for testing

### WARNING: demonstration, research, development and testing purposes ONLY!
if you need working stuff: https://github.com/facebookarchive/doh-proxy

## requirements
- `dnspython` `json` `urllib`

to install these for user, use:
```bash
$ pip3 install --break-system-packages --user [MODULES...]
```

## What are all of these?

### client-side:
- [X] `doh-client.py` - **DoH** client, command-line

### server-side (a.k.a `stub`):
- [X] `dns-query.py` - **DoH** server, CGI (Apache), NOTE: running with no arguments starts this mode!
- [ ] `?dns-query-fcgi.py?` - **DoH** server, FastCGI, talking through `fcgi.sock`
- [ ] `?` - **DoH** server, WSGI/ASGI w/e this is...
- [?] `?` - **DoH** server, standalone or reverse-proxy, if FCGI/WSGI/ASGI stuff feels slow
- [?] `?` - **DoH** server in C/C++, if `python3` feels slow
- [?] ...wrap every example, so that it can `serve_forever()`

### other:
- `dns-query.conf` - Apache CGI `conf.d/` drop-in example

## What are all of these FOR???!!!
- plain-DNS queries over `:53/udp` is not secure, can't be trusted and leak data
- *opt. 0:* DNS-over-TLS to `:853/tcp` can be used to trusted nameservers (cuddleflare, oogle)
- *opt. 1:* setup **DoH-proxy** on router and block **outgoing** connections in firewall on your router
- *opt. 2:* setup encrypted WireGuard tunnel to some VPS/VDS and use it's nameserver as the primary one

## Examples
query is DNS-wire message in modified base64, see:
https://github.com/dohwg/draft-ietf-doh-dns-over-https/issues/30#issuecomment-345850479

**FIXME:** you can get such b64 string like this:
```bash
$ nc -lu 10053 | base64 | sed '/[=]+$//g' | tr '+=' '_/' </dev/null &
$ dig github.com -p 10053 @127.0.0.1 &>/dev/null 2>&1
```

`name=` is (non-RFC) addition for debugging
```bash
$ ./doh-client.py name=github.com
```

`/dev/stdin` is read to answer POST requests, hence `</dev/null`
```bash
$ ./dns-query.py dns=AAABAAABAAAAAAAABmdpdGh1YgNjb20AAAEAAQ </dev/null
$ QUERY_STRING=dns=AAABAAABAAAAAAAABmdpdGh1YgNjb20AAAEAAQ ./dns-query.py </dev/null
$ echo dns=AAABAAABAAAAAAAABmdpdGh1YgNjb20AAAEAAQ | ./dns-query.py
```

## Links
- WGSI: https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface
- Caddy FastCGI example: https://github.com/tonyallan/python3-experiments/tree/main/caddy-server-fastcgi

## LICENSE
- Public Domain


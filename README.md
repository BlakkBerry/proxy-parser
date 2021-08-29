# How to use?

**positional arguments:**\
  ` file` - file path for saving proxies

**optional arguments:**\
  `-h, --help` - show this help message and exit\
  `-t, --types` - proxies' types list (http, https, socks4 and/or socks5)\
  `-a, --anon` - proxy anonymity scale (high, avg, low)\
  `-p, --ports` - proxies ports\
  `-v, --validate` - if specified, invalid proxies will be skipped\
  `-T, --timeout, --time` - max time to mark proxy as *'invalid'*. Not needed if -v (validate) flag is not specified.\
  `-l, --logging` - path to save a logging file. If not specified the logging file won't be created.
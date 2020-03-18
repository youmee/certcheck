# Certcheck

Certcheck will do inspection of http/s redirections and SSL installation.

## Requirements:
Python 3.6+
- [aiohttp](https://docs.aiohttp.org/) for async HTTP requests 
- [colored](https://pypi.org/project/colored/) for colored console output

## Installation
```shell script
pip install certcheck
```

## Documentation
For documentation use `$ certcheck --help`.

## Usage
```shell script
$ certcheck -d google.com
Certcheck 0.1
Running for domain: google.com
============================== 
http://google.com                --- 301 MOVED PERMANENTLY (http://www.google.com/)
http://www.google.com            --- 200 OK
https://google.com               --- 301 MOVED PERMANENTLY (https://www.google.com/)
https://www.google.com           --- 200 OK
Done in 209 ms.
```


## License

This project is licensed under the terms of the MIT license.
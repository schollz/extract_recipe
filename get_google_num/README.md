# Crawling anonymously with Tor

This is from [this website](http://sacharya.com/crawling-anonymously-with-tor-in-python/)
[Archived](https://web.archive.org/web/20150213193312/http://sacharya.com/crawling-anonymously-with-tor-in-python/)
Install tor

```
sudo pip install pysocks
sudo apt-get install tor
```
You will notice that socks listener is on port 9050.

Lets enable the ControlPort listener for Tor to listen on port 9051. This is the port Tor will listen to for any communication from applications talking to Tor controller. The Hashed password is to enable authentication to the port to prevent any random access to the port.

You can create a hashed password out of your password using:

```
tor --hash-password mypassword
```
So, update the torrc with the port and the hashed password.

/etc/tor/torrc


```
ControlPort 9051
HashedControlPassword 16:872860B76453A77D60CA2BB8C1A7042072093276A3D701AD684053EC4C
```
Restart Tor again to the configuration changes are applied.

```
/etc/init.d/tor restart
```

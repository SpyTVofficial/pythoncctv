
# Python CCTV

The goal of this project is, to be able to use any old PC as a CCTV Station. There are two sides to this, a 'server' and a 'client.

## Server

The Server's goal is to receive all of the Client's video streams and show them in one simple Webinterface. The User should also be able to save them.
Motion Detection is also planned, but might be a bit difficult to implement.

## Client

The Client's goal is to send the video stream to the Server. It should also be able to detect movement and send a notification to the Server.

    
## Run Locally

Clone the project

```bash
  git clone https://github.com/SpyTVofficial/pythoncctv.git
```

Go to the project directory

```bash
  cd pythoncctv
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the Server

```bash
  py cctv.py server
```

Start the Client
```bash
  py cctv.py client
``` 
And enter the IP-Adress of the Server
```bash
  Enter IP address (press Enter for default): 
```
## Todo

- HTTP Login
- ~~Showing Video Stream on Webserver~~
- Saving Video Stream
- Movement Detection

## Roadmap

- Central Management Place


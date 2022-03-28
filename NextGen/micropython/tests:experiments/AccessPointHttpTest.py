import network,select,socket,esp,utime

esp.osdebug(None)       # turn off vendor O/S debugging messages

if 'ap' not in globals():
	ap = network.WLAN(network.AP_IF)
	ap.active(True)
	ap.config(essid="MicropythonRyan")#, password=None)

if 'ap_if' not in globals():
	ap_if = network.WLAN(network.AP_IF)#"WIFI LocalAreaNetwork" "Access Point InterFace"
	my_ip_address,my_netmask,my_gateway,my_dns=ap_if.ifconfig()
print("My IP Address:",my_ip_address)#My IP Address: 192.168.4.1 <-- It always gives this IP

if 's' not in globals():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((my_ip_address, 80))
	s.listen(5)#s.listen(backlog) where backlog is the maximum number of unaccepted connections (we have to specify this number in micropython)

while True:
  conn, addr = s.accept()
  print('Got a connection from %s' % str(addr))
  request = conn.recv(1024)#You can call this again if you want to...but hopefully none of me messages will be that long...

  response=handle_request(request.decode())
  if response is None:
  	response='(Default Response)'
  # print("REQUEST:",(request))
  # print('Content = %s' % str(request))
  # response ="hellloooo this is a response durrrr"# web_page()
  conn.send(response)
  conn.close()

def handle_request(request:str)->str:
	if request.startswith('GET /'):
		url_path=request[5:]
		url_path=url_path[:url_path.find(' ')]
		url_path=url_path.split('/')
		handle_url_path(*url_path)

def handle_url_path(*url_path)->str:
	return str("TIME IN MILLIS:",utime.ticks_ms())


# p=select.poll()
# p.register(s,select.POLLIN)# POLLIN: Available for read


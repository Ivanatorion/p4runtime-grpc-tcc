import socket

# Contains functions to decode byte strings into Ethernet, IPv4 and port addresses.

def matchesMac(mac_addr_string):
	if len(mac_addr_string) == 12:
		return True
	else: 
		return False

def decodeMac(encoded_mac_addr):
    return ":".join(s.encode("hex") for s in encoded_mac_addr)

def matchesIPv4(ip_addr_string):
    if len(ip_addr_string) == 8:
    	return True
    else:
    	return False

def decodeIPv4(encoded_ip_addr):
    return socket.inet_ntoa(encoded_ip_addr)

def matchesPort(port_number):
	if len(port_number) == 4:
		return True
	else:
		return False

def decodePort(encoded_port_number):
	if int(encoded_port_number) == 1:
		return "0b00000001"
	elif int(encoded_port_number) == 2:
		return "0b00000100"
	elif int(encoded_port_number) == 3:
		return "0b00010000"
	elif int(encoded_port_number) == 4:
		return "0b01000000"

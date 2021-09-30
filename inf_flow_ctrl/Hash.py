import hashlib

class Hash():

	@staticmethod
	def packet_to_hash(packet):
		packetS = str(packet)
		hash = hashlib.sha256(packetS).hexdigest()
		return hash

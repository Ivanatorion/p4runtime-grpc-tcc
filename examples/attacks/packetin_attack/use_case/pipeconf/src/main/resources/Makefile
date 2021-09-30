all: l2_switch

mytunnel: l2_switch.p4
	p4c-bm2-ss --arch v1model -o l2_switch.json \
		--p4runtime-files l2_switch_p4info.txt \
		l2_switch.p4

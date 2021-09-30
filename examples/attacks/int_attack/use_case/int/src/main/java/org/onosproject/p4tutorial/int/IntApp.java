/*
 * Copyright 2017-present Open Networking Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.onosproject.p4tutorial.mytunnel;

import com.google.common.collect.ImmutableList;
import org.onlab.packet.*;
import org.onlab.util.ImmutableByteSequence;
import org.onosproject.mastership.MastershipService;
import org.onosproject.net.device.DeviceService;
import org.onosproject.net.flow.*;
import org.onosproject.net.flow.criteria.PiCriterion;
import org.onosproject.net.packet.*;
import org.onosproject.net.pi.model.PiActionId;
import org.onosproject.net.pi.model.PiActionParamId;
import org.onosproject.net.pi.model.PiMatchFieldId;
import org.onosproject.net.pi.model.PiPipelineInterpreter;
import org.onosproject.net.pi.runtime.PiAction;
import org.onosproject.net.pi.runtime.PiActionParam;
import org.onosproject.net.pi.runtime.PiPacketMetadata;
import org.onosproject.net.pi.runtime.PiPacketOperation;
import org.osgi.service.component.annotations.Activate;
import org.osgi.service.component.annotations.Component;
import org.osgi.service.component.annotations.Deactivate;
import org.osgi.service.component.annotations.Reference;
import org.osgi.service.component.annotations.ReferenceCardinality;
import org.onosproject.core.ApplicationId;
import org.onosproject.core.CoreService;
import org.onosproject.net.DeviceId;
import org.onosproject.net.Host;
import org.onosproject.net.PortNumber;
import org.onosproject.net.host.HostEvent;
import org.onosproject.net.host.HostListener;
import org.onosproject.net.host.HostService;
import org.onosproject.net.topology.TopologyService;
import org.slf4j.Logger;

import java.io.UnsupportedEncodingException;
import java.nio.ByteBuffer;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Collections;
import java.util.Optional;

import static org.onlab.util.ImmutableByteSequence.copyFrom;
import static org.onosproject.net.pi.model.PiPacketOperationType.PACKET_OUT;
import static org.slf4j.LoggerFactory.getLogger;


@Component(immediate = true)
public class IntApp {

    private static final String APP_NAME = "org.onosproject.p4tutorial.mytunnel";

    // Default priority used for flow rules installed by this app.
    private static final int FLOW_RULE_PRIORITY = 100;

    private final HostListener hostListener = new InternalHostListener();
    private ApplicationId appId;

    private static final Logger log = getLogger(IntApp.class);

    private ReactivePacketProcessor processor = new ReactivePacketProcessor();

    //--------------------------------------------------------------------------
    // ONOS core services needed by this application.
    //--------------------------------------------------------------------------

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    private FlowRuleService flowRuleService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    private CoreService coreService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    private TopologyService topologyService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    private HostService hostService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    protected PacketService packetService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    private MastershipService mastershipService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    private DeviceService deviceService;


    //--------------------------------------------------------------------------
    //--------------------------------------------------------------------------

    @Activate
    public void activate() {
        // Register app and event listeners.
        log.info("Starting...");
        appId = coreService.registerApplication(APP_NAME);
        hostService.addListener(hostListener);
        log.info("STARTED", appId.id());
        TrafficSelector.Builder selector = DefaultTrafficSelector.builder();
        //packetService.requestPackets(selector.build(), PacketPriority.REACTIVE, appId);
        packetService.addProcessor(processor, PacketProcessor.director(2));
    }

    @Deactivate
    public void deactivate() {
        // Remove listeners and clean-up flow rules.
        log.info("Stopping...");
        hostService.removeListener(hostListener);
        flowRuleService.removeFlowRulesById(appId);
        log.info("STOPPED");
    }

    private class ReactivePacketProcessor implements PacketProcessor{

        @Override
        public void process(PacketContext context) {
            if(context.isHandled()){
                return;
            }

            InboundPacket pkt = context.inPacket();

            Ethernet eth = pkt.parsed();
            ByteBuffer packet_data = pkt.unparsed();
            IPacket ipacket = eth.getPayload();
            Optional<Long> ckie = context.inPacket().cookie();;
            String cookie_string = String.valueOf(ckie);
            int startIndex1 = cookie_string.indexOf("[");
            int endIndex1 = cookie_string.indexOf("]");
            String cookie_substring = cookie_string.substring(startIndex1+1, endIndex1);

            
            String test = String.valueOf(ipacket);
            if(test.contains("options")){
                int startIndex = test.indexOf("[");
                int endIndex = test.indexOf("]");

                String substr_packet = test.substring(startIndex, endIndex);
                log.info(substr_packet);
                //for(int i=0; i<=substr_packet.length()-1; i++){
                //    log.info(substr_packet.charAt(i) + String.valueOf(i));
                //}
                Integer qdepth1 = null;

                Integer tripledigit = Integer.valueOf(substr_packet.substring(57, 58));
                if(tripledigit >= 1){
                    qdepth1 = Integer.parseInt(cookie_substring);
                }
                else{
                    qdepth1 = Integer.valueOf(substr_packet.substring(60, 63));
                }

                Integer switch_id1 = Integer.valueOf(substr_packet.substring(48, 49));
                Integer switch_id2 = Integer.valueOf(substr_packet.substring(24, 25));
                Integer qdepth2 = Integer.valueOf(substr_packet.substring(36, 37));

                String newLine = System.getProperty("line.separator");
                log.info("####### [ INT ] ######" + newLine +
                        "           ### [ SwitchTrace ] ###" + newLine +
                        "               swid = " + switch_id1 + newLine +
                        "               qdepth = " + qdepth1 + newLine +
                        "           ### [ SwitchTrace ] ###" + newLine +
                        "               swid = " + switch_id2 + newLine +
                        "               qdepth = " + qdepth2 + newLine);

                if(qdepth1 >= 100){
                    log.info("Queue Depth is way too high, blocking flow from the switch..");
                    insertFlowRule(DeviceId.deviceId("device:bmv2:s2"));
                }
                else {
                    log.info("Number of Queue Depth is normal");
                }

            }


        }

        private void insertFlowRule(DeviceId deviceId){

            final int table_id = 0;
            Ip4Address ip4Prefix = Ip4Address.valueOf("10.0.2.22");
            IpAddress dstPkt = IpAddress.valueOf("10.0.2.22");
            //ip4Prefix = Ip4Address.valueOf("10.0.2.22");
            final PiCriterion match = PiCriterion.builder()
                    .matchLpm(PiMatchFieldId.of("hdr.ipv4.dstAddr"), dstPkt.toOctets() , 32)
                    .build();
            PortNumber portNumber = PortNumber.portNumber("4");
            final PiAction setAct = PiAction.builder()
                    .withId(PiActionId.of("MyIngress.ipv4_forward"))
                    .withParameter(new PiActionParam(PiActionParamId.of("port"), (short) portNumber.toLong()))
                    .withParameters(Collections.singleton(new PiActionParam(PiActionParamId.of("dstAddr"), MacAddress.valueOf("08:00:00:00:02:22").toBytes())))
                    .build();
            FlowRule rule = DefaultFlowRule.builder()
                    .forDevice(deviceId)
                    .forTable(table_id)
                    .fromApp(appId)
                    .withSelector(DefaultTrafficSelector.builder()
                            .matchPi(match).build())
                    .withTreatment(DefaultTrafficTreatment.builder()
                            .piTableAction(setAct).build())
                    .makePermanent()
                    .withPriority(FLOW_RULE_PRIORITY)
                    .build();
            flowRuleService.applyFlowRules(rule);
        }


    }



    /**
     * A listener of host events that provisions two tunnels for each pair of
     * hosts when a new host is discovered.
     */
    private static class InternalHostListener implements HostListener {

        @Override
        public void event(HostEvent event) {
            if (event.type() != HostEvent.Type.HOST_ADDED) {
                // Ignore other host events.
                return;
            }
            synchronized (this) {
                // Synchronizing here is an overkill, but safer for demo purposes.
                //sendDummy();
                final Host host = event.subject();
                final DeviceId deviceId = host.location().deviceId();
                final PortNumber port = host.location().port();
                //learnHost(host, deviceId, port);
            }
        }
    }


}

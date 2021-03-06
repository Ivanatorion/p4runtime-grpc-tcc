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

package org.onosproject.p4tutorial.pipeconf;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import org.onlab.packet.DeserializationException;
import org.onlab.packet.Ethernet;
import org.onlab.util.ImmutableByteSequence;
import org.onosproject.net.ConnectPoint;
import org.onosproject.net.DeviceId;
import org.onosproject.net.Port;
import org.onosproject.net.PortNumber;
import org.onosproject.net.device.DeviceService;
import org.onosproject.net.driver.AbstractHandlerBehaviour;
import org.onosproject.net.flow.TrafficTreatment;
import org.onosproject.net.flow.criteria.Criterion;
import org.onosproject.net.flow.instructions.Instruction;
import org.onosproject.net.flow.instructions.Instructions.OutputInstruction;
import org.onosproject.net.packet.*;
import org.onosproject.net.pi.model.PiActionId;
import org.onosproject.net.pi.model.PiActionParamId;
import org.onosproject.net.pi.model.PiMatchFieldId;
import org.onosproject.net.pi.model.PiPacketMetadataId;
import org.onosproject.net.pi.model.PiPipelineInterpreter;
import org.onosproject.net.pi.model.PiTableId;
import org.onosproject.net.pi.runtime.PiAction;
import org.onosproject.net.pi.runtime.PiActionParam;
import org.onosproject.net.pi.runtime.PiPacketMetadata;
import org.onosproject.net.pi.runtime.PiPacketOperation;

import java.nio.ByteBuffer;
import java.util.*;

import static java.lang.Long.parseLong;
import static org.onosproject.net.PortNumber.*;
import static com.google.common.base.Preconditions.checkState;
import static java.lang.String.format;
import static org.onlab.util.ImmutableByteSequence.copyFrom;
import static org.onosproject.alarm.XmlEventParser.log;
import static org.onosproject.net.flow.instructions.Instruction.Type.OUTPUT;
import static org.onosproject.net.pi.model.PiPacketOperationType.PACKET_OUT;

/**
 * Implementation of a pipeline interpreter for the mytunnel.p4 program.
 */
public final class PipelineInterpreterImpl
        extends AbstractHandlerBehaviour
        implements PiPipelineInterpreter {

    private static final String DOT = ".";
    private static final String HDR = "hdr";
    private static final String C_INGRESS = "MyIngress";
    private static final String T_IPV4_FWD = "ipv4_lpm";
    private static final String EGRESS_PORT = "egress_port";
    private static final String INGRESS_PORT = "ingress_port";
    private static final String IPV4 = "ipv4";
    private static final String ETHERNET = "ethernet";
    private static final String STANDARD_METADATA = "standard_metadata";
    private static final int PORT_FIELD_BITWIDTH = 9;

    private static final PiMatchFieldId INGRESS_PORT_ID =
            PiMatchFieldId.of(STANDARD_METADATA + DOT + "ingress_port");
    private static final PiMatchFieldId ETH_DST_ID =
            PiMatchFieldId.of(HDR + DOT + ETHERNET + DOT + "dstAddr");
    private static final PiMatchFieldId ETH_SRC_ID =
            PiMatchFieldId.of(HDR + DOT + ETHERNET + DOT + "srcAddr");
    private static final PiMatchFieldId ETH_TYPE_ID =
            PiMatchFieldId.of(HDR + DOT + ETHERNET + DOT + "etherType");
    private static final PiMatchFieldId IPV4_DST_ID =
            PiMatchFieldId.of(HDR + DOT + IPV4 + DOT + "dstAddr");
    private static final PiMatchFieldId IPV4_SRC_ID =
            PiMatchFieldId.of(HDR + DOT + IPV4 + DOT + "srcAddr");

    private static final PiTableId TABLE_IPV4_ID =
            PiTableId.of(C_INGRESS + DOT + T_IPV4_FWD);

    private static final PiActionId ACT_ID_NOP =
            PiActionId.of("NoAction");
    private static final PiActionId ACT_ID_SEND_TO_CPU =
            PiActionId.of(C_INGRESS + DOT + "send_to_cpu");
    private static final PiActionId ACT_ID_IPV4_FORWARD =
            PiActionId.of(C_INGRESS + DOT + "ipv4_forward");

    private static final PiActionParamId ACT_PARAM_ID_PORT =
            PiActionParamId.of("port");
    private static final PiActionParamId ACT_PARAM_DST_ADDR =
            PiActionParamId.of("dstAddr");

    private static final Map<Integer, PiTableId> TABLE_MAP =
            new ImmutableMap.Builder<Integer, PiTableId>()
                    .put(0, TABLE_IPV4_ID)
                    .build();

    private static final Map<Criterion.Type, PiMatchFieldId> CRITERION_MAP =
            ImmutableMap.<Criterion.Type, PiMatchFieldId>builder()
                    .put(Criterion.Type.IN_PORT, INGRESS_PORT_ID)
                    .put(Criterion.Type.IPV4_DST, IPV4_DST_ID)
                    .put(Criterion.Type.ETH_DST, ETH_DST_ID)
                    .put(Criterion.Type.ETH_SRC, ETH_SRC_ID)
                    .put(Criterion.Type.ETH_TYPE, ETH_TYPE_ID)
                    .build();

    public PiPacketOperation pkt_in;
    public PortNumber portNum;

    @Override
    public Optional<PiMatchFieldId> mapCriterionType(Criterion.Type type) {
        return Optional.ofNullable(CRITERION_MAP.get(type));
    }

    @Override
    public Optional<PiTableId> mapFlowRuleTableId(int flowRuleTableId) {
        return Optional.ofNullable(TABLE_MAP.get(flowRuleTableId));
    }

    @Override
    public PiAction mapTreatment(TrafficTreatment treatment, PiTableId piTableId)
            throws PiInterpreterException {

        if (piTableId != TABLE_IPV4_ID) {
            throw new PiInterpreterException(
                    "Can map treatments only for 't_l2_fwd' table");
        }

        if (treatment.allInstructions().size() == 0) {
            // 0 instructions means "NoAction"
            return PiAction.builder().withId(ACT_ID_NOP).build();
        } else if (treatment.allInstructions().size() > 1) {
            // We understand treatments with only 1 instruction.
            throw new PiInterpreterException("Treatment has multiple instructions");
        }

        // Get the first and only instruction.
        Instruction instruction = treatment.allInstructions().get(0);

        if (instruction.type() != OUTPUT) {
            // We can map only instructions of type OUTPUT.
            throw new PiInterpreterException(format(
                    "Instruction of type '%s' not supported", instruction.type()));
        }

        OutputInstruction outInstruction = (OutputInstruction) instruction;
        PortNumber port = outInstruction.port();
        if (!port.isLogical()) {
            return PiAction.builder()
                    .withId(ACT_ID_IPV4_FORWARD)
                    .withParameter(new PiActionParam(
                            ACT_PARAM_ID_PORT, copyFrom(port.toLong())))
                    .build();
        } else if (port.equals(CONTROLLER)) {
            return PiAction.builder()
                    .withId(ACT_ID_SEND_TO_CPU)
                    .build();
        } else {
            throw new PiInterpreterException(format(
                    "Output on logical port '%s' not supported", port));
        }
    }

    @Override
    public Collection<PiPacketOperation> mapOutboundPacket(OutboundPacket packet)
            throws PiInterpreterException {

        TrafficTreatment treatment = packet.treatment();

        // We support only packet-out with OUTPUT instructions.
        if (treatment.allInstructions().size() != 1 &&
                treatment.allInstructions().get(0).type() != OUTPUT) {
            throw new PiInterpreterException(
                    "Treatment not supported: " + treatment.toString());
        }

        Instruction instruction = treatment.allInstructions().get(0);
        PortNumber port = ((OutputInstruction) instruction).port();
        List<PiPacketOperation> piPacketOps = Lists.newArrayList();

        if (!port.isLogical()) {
            piPacketOps.add(createPiPacketOp(packet.data(), port.toLong()));
        } else if (port.equals(FLOOD)) {
            DeviceService deviceService = handler().get(DeviceService.class);
            DeviceId deviceId = packet.sendThrough();
            for (Port p : deviceService.getPorts(deviceId)) {
                piPacketOps.add(createPiPacketOp(packet.data(), p.number().toLong()));
            }
        } else {
            throw new PiInterpreterException(format(
                    "Output on logical port '%s' not supported", port));
        }

        return piPacketOps;
    }


    @Override
    public DefaultInboundPacket mapInboundPacket(PiPacketOperation packetIn, DeviceId deviceId)
            throws PiInterpreterException {

        Ethernet ethPkt;
        this.pkt_in = packetIn;

        try {
            ethPkt = Ethernet.deserializer().deserialize(
                    packetIn.data().asArray(), 0, packetIn.data().size());
        } catch (DeserializationException dex) {
            throw new PiInterpreterException(dex.getMessage());
        }
        log.warn("Packet-in arrived from the switch");
        //log.info(String.valueOf(packetIn));
        String hexpkt = String.valueOf(packetIn.data());
        //for(int i=0; i<=hexpkt.length()-1; i++){
        //    log.info(hexpkt.charAt(i) + String.valueOf(i));
        //}
        String hexvalue = hexpkt.substring(106, 109);
        int hexvalue_int = Integer.parseInt(hexvalue, 16);
        Long l = (long) hexvalue_int;
        //Long cookie = parseLong("fa0"); //4000
        String other = "190"; //400



        // Returns the ingress port packet metadata.
        Optional<PiPacketMetadata> packetMetadata = packetIn.metadatas().stream()
                .filter(metadata -> metadata.id().toString().equals(INGRESS_PORT))
                .findFirst();
        if (packetMetadata.isPresent()) {
            short s = packetMetadata.get().value().asReadOnlyBuffer().getShort();
            ConnectPoint receivedFrom = new ConnectPoint(
                    deviceId, PortNumber.portNumber(s));
            createPiPacketOp((packetIn.data().asReadOnlyBuffer()), PortNumber.portNumber(s).toLong());
            this.portNum = PortNumber.portNumber(s);
            return new DefaultInboundPacket(
                    receivedFrom, ethPkt, packetIn.data().asReadOnlyBuffer(), Optional.of(l));
            //Optional.of(cookie
        } else {
            throw new PiInterpreterException(format(
                    "Missing metadata '%s' in packet-in received from '%s': %spkt.data();",
                    INGRESS_PORT, deviceId, packetIn));
        }
    }



    private PiPacketOperation createPiPacketOp(ByteBuffer data, long portNumber)
            throws PiInterpreterException {
        PiPacketMetadata metadata = createPacketMetadata(1);
        return PiPacketOperation.builder()
                .withType(PACKET_OUT)
                .withData(copyFrom(data))
                .withMetadatas(ImmutableList.of(metadata))
                .build();
    }

    private PiPacketMetadata createPacketMetadata(long portNumber)
            throws PiInterpreterException {
        try {
            return PiPacketMetadata.builder()
                    .withId(PiPacketMetadataId.of(EGRESS_PORT))
                    .withValue(copyFrom(portNumber).fit(PORT_FIELD_BITWIDTH))
                    .build();
        } catch (ImmutableByteSequence.ByteSequenceTrimException e) {
            throw new PiInterpreterException(format(
                    "Port number %d too big, %s", portNumber, e.getMessage()));
        }
    }
}

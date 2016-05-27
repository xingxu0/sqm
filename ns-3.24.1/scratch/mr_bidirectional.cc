#include "ns3/lte-helper.h"
#include "ns3/epc-helper.h"
#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/ipv4-global-routing-helper.h"
#include "ns3/internet-module.h"
#include "ns3/mobility-module.h"
#include "ns3/lte-module.h"
#include "ns3/applications-module.h"
#include "ns3/point-to-point-helper.h"
#include "ns3/config-store.h"
#include "ns3/data-rate.h"
#include "ns3/point-to-point-net-device.h"
#include "ns3/radio-environment-map-helper.h"
#include "../src/lte/model/weight-table.h"
#include "ns3/flow-monitor-module.h"
#include <ns3/flow-monitor-helper.h>
#include <vector>
#include <stdlib.h> 
#include <sstream>
#include <stdio.h>      /* printf, scanf, puts, NULL */
#include <stdlib.h>     /* srand, rand */
#include <time.h>  
#include <math.h>       /* sin */
#include <ns3/lte-amc.h>
#define PI 3.14159265

using namespace ns3;

uint16_t numberOfNodes = 30;

NS_LOG_COMPONENT_DEFINE ("LTEExample");

void ThroughputMonitor (FlowMonitorHelper *fmhelper, Ptr<FlowMonitor> flowMon)
{
	std::map<FlowId, FlowMonitor::FlowStats> flowStats = flowMon->GetFlowStats();
	Ptr<Ipv4FlowClassifier> classing = DynamicCast<Ipv4FlowClassifier> (fmhelper->GetClassifier());
	for (std::map<FlowId, FlowMonitor::FlowStats>::const_iterator stats = flowStats.begin (); stats != flowStats.end (); ++stats)
	{
		Ipv4FlowClassifier::FiveTuple fiveTuple = classing->FindFlow (stats->first);
		std::cout<<"Flow ID			: " << stats->first <<" ; "<< fiveTuple.sourceAddress <<" -----> "<<fiveTuple.destinationAddress<<std::endl;
		std::cout<<"Tx Packets = " << stats->second.txPackets<<std::endl;
		std::cout<<"Tx Bytes = " << stats->second.txBytes<<std::endl;
		std::cout<<"Rx Packets = " << stats->second.rxPackets<<std::endl;
		std::cout<<"Rx Bytes = " << stats->second.rxBytes<<std::endl;
		std::cout<<"Duration		: "<<stats->second.timeLastTxPacket.GetSeconds()-stats->second.timeFirstTxPacket.GetSeconds()<<std::endl;
		std::cout<<"Last Received Packet	: "<< stats->second.timeLastTxPacket.GetSeconds()<<" Seconds"<<std::endl;
		std::cout<<"Lost Packet : "<< stats->second.lostPackets<<std::endl;
		std::cout<<"Throughput: " << stats->second.rxBytes*1.0/(stats->second.timeLastRxPacket.GetSeconds()-stats->second.timeFirstRxPacket.GetSeconds()) << " B/s"<<std::endl;
		std::cout<<"---------------------------------------------------------------------------"<<std::endl;
	}
	Simulator::Schedule(Seconds(1),&ThroughputMonitor, fmhelper, flowMon);
}

int main (int argc, char *argv[])
{
	double simTime = 10;
	double distance = 1000.0;
	double interPacketInterval = 0.01;
	double interSiteDistance = 2000;
	int ack = 1;
	int interval_ul = 0;
	
	CommandLine cmd;
	cmd.AddValue("ack", "ack", ack);
	cmd.AddValue("interval_ul", "interval_ul", interval_ul);
	
	cmd.Parse(argc, argv);
	ConfigStore config;
	config.ConfigureDefaults ();
	
	Ptr<LteHelper> lteHelper = CreateObject<LteHelper> ();
	lteHelper->SetAttribute ("PathlossModel", StringValue ("ns3::FriisPropagationLossModel"));
	Ptr<PointToPointEpcHelper> epcHelper = CreateObject<PointToPointEpcHelper> ();
	lteHelper->SetEpcHelper (epcHelper);
	Ptr<LteEnbRrc> rrc = CreateObject<LteEnbRrc> ();
	if (ack == 1) {
		rrc->SetAttribute ("EpsBearerToRlcMapping", EnumValue (LteEnbRrc::RLC_AM_ALWAYS));
		Config::SetDefault ("ns3::LteEnbRrc::EpsBearerToRlcMapping",EnumValue(LteEnbRrc::RLC_AM_ALWAYS));
 	}

 	ConfigStore inputConfig;
	inputConfig.ConfigureDefaults();
	cmd.Parse(argc, argv);

	Ptr<Node> pgw = epcHelper->GetPgwNode ();

	NodeContainer remoteHostContainer;
	remoteHostContainer.Create (numberOfNodes);

	InternetStackHelper internet;
	internet.Install (remoteHostContainer);

	std::vector<PointToPointHelper*> p2pv;
	// Create the internet
	Ipv4StaticRoutingHelper ipv4RoutingHelper;
	NetDeviceContainer internetDevices;
	std::vector<NetDeviceContainer> ndc;
	std::vector<Ipv4InterfaceContainer> internetIpIfacesv;
	for (uint16_t i = 0; i < numberOfNodes; i++) {
		PointToPointHelper* p2ph = new PointToPointHelper();
		p2ph->SetDeviceAttribute ("DataRate", DataRateValue (DataRate ("10Mb/s")));
		p2ph->SetDeviceAttribute ("Mtu", UintegerValue (1500));
		p2ph->SetChannelAttribute ("Delay", TimeValue (Seconds (interPacketInterval)));

		Ptr<Node> remoteHost = remoteHostContainer.Get (i);
		internetDevices = p2ph->Install (pgw, remoteHost);
		Ipv4AddressHelper ipv4h;
		char buf[512];
		sprintf(buf,"1.0.%d.0", i);
		ipv4h.SetBase (buf, "255.255.255.0");
		Ipv4InterfaceContainer internetIpIfaces = ipv4h.Assign (internetDevices);
		internetIpIfaces.GetAddress (1);
		Ptr<Ipv4StaticRouting> remoteHostStaticRouting = ipv4RoutingHelper.GetStaticRouting (remoteHost->GetObject<Ipv4> ());
		remoteHostStaticRouting->AddNetworkRouteTo (Ipv4Address ("7.0.0.0"), Ipv4Mask ("255.0.0.0"), 1);

		p2pv.push_back(p2ph);
		ndc.push_back(internetDevices);
		internetIpIfacesv.push_back(internetIpIfaces);
	}

	LogLevel logLevel = (LogLevel)(LOG_PREFIX_FUNC | LOG_PREFIX_TIME | LOG_LEVEL_ALL);

	LogComponentEnable ("LteHelper", logLevel);
	LogComponentEnable ("EpcHelper", logLevel);
	LogComponentEnable ("EpcEnbApplication", logLevel);
	LogComponentEnable ("EpcSgwPgwApplication", logLevel);
	LogComponentEnable ("EpcMme", logLevel);
	LogComponentEnable ("LteEnbRrc", logLevel);
	LogComponentEnable ("EpcUeNas", logLevel);

	NodeContainer ueNodes;
	NodeContainer enbNodes;
	enbNodes.Create(1);
	ueNodes.Create(numberOfNodes);

	// Install Mobility Model
	Ptr<ListPositionAllocator> positionAlloc = CreateObject<ListPositionAllocator> ();

	for (uint16_t i = 0; i < numberOfNodes; i++)
		positionAlloc->Add (Vector(distance, 0, 0));

	MobilityHelper mobility;
	mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
	mobility.Install(enbNodes);
	mobility.SetPositionAllocator(positionAlloc);

	mobility.Install(ueNodes);

	Ptr<LteHexGridEnbTopologyHelper> lteHexGridEnbTopologyHelper = CreateObject<LteHexGridEnbTopologyHelper> ();
	lteHexGridEnbTopologyHelper->SetLteHelper (lteHelper);
	
	lteHexGridEnbTopologyHelper->SetAttribute ("InterSiteDistance", DoubleValue (interSiteDistance));
	lteHexGridEnbTopologyHelper->SetAttribute ("MinX", DoubleValue (0));//-1000));
	lteHexGridEnbTopologyHelper->SetAttribute ("MinY", DoubleValue (0));//-1732));
	lteHexGridEnbTopologyHelper->SetAttribute ("GridWidth", UintegerValue (2));
	
	lteHelper->SetEnbAntennaModelType ("ns3::ParabolicAntennaModel");
	lteHelper->SetEnbAntennaModelAttribute ("Beamwidth",   DoubleValue (70));
	lteHelper->SetEnbAntennaModelAttribute ("MaxAttenuation",     DoubleValue (20.0));
	 
	lteHelper->SetEnbDeviceAttribute ("DlBandwidth", UintegerValue (25));
	lteHelper->SetEnbDeviceAttribute ("UlBandwidth", UintegerValue (25));
	NetDeviceContainer enbLteDevs = lteHexGridEnbTopologyHelper->SetPositionAndInstallEnbDevice (enbNodes);
	NetDeviceContainer ueLteDevs = lteHelper->InstallUeDevice (ueNodes);

	// Install the IP stack on the UEs
	internet.Install (ueNodes);
	Ipv4InterfaceContainer ueIpIface;
	ueIpIface = epcHelper->AssignUeIpv4Address (NetDeviceContainer (ueLteDevs));

	// Assign IP address to UEs, and install applications
	for (uint32_t u = 0; u < ueNodes.GetN (); ++u)
	{
		Ptr<Node> ueNode = ueNodes.Get (u);
		// Set the default gateway for the UE
		Ptr<Ipv4StaticRouting> ueStaticRouting = ipv4RoutingHelper.GetStaticRouting (ueNode->GetObject<Ipv4> ());
		ueStaticRouting->SetDefaultRoute (epcHelper->GetUeDefaultGatewayAddress (), 1);
	}

	for (uint16_t i = 0; i < numberOfNodes; i++)
	{
		lteHelper->Attach (ueLteDevs.Get(i));
	}  

	// Install and start applications on UEs and remote host
	uint16_t dlPort = 33333;
	uint16_t ulPort = 2000;
	uint16_t otherPort = 3000;
	ApplicationContainer clientApps;
	ApplicationContainer serverApps;
	ApplicationContainer ulclientApps;
	for (uint32_t u = 0; u < ueNodes.GetN (); ++u)
	{
		++ulPort;
		++otherPort;
		PacketSinkHelper dlPacketSinkHelper ("ns3::TcpSocketFactory", InetSocketAddress (Ipv4Address::GetAny (), dlPort));
		serverApps.Add (dlPacketSinkHelper.Install (ueNodes.Get(u)));

		UdpClientHelper dlClient (ueIpIface.GetAddress (u), dlPort);
		dlClient.SetAttribute ("Interval", TimeValue (MilliSeconds(1)));
		dlClient.SetAttribute ("MaxPackets", UintegerValue(10000000));
		Ptr<Node> remoteHost = remoteHostContainer.Get (u);
		clientApps.Add(dlClient.Install(remoteHost));

		if (interval_ul) {
			Ptr<Node> remoteHost = remoteHostContainer.Get (u);
			UdpClientHelper ulClient (internetIpIfacesv[u].GetAddress (1), ulPort);
			ulClient.SetAttribute ("Interval", TimeValue (MilliSeconds(interval_ul)));
			ulClient.SetAttribute ("MaxPackets", UintegerValue(1000000));
			ulclientApps.Add (ulClient.Install (ueNodes.Get(u)));
		}
	}
	serverApps.Start (Seconds (1.0));
	clientApps.Start (Seconds (1.0));
	if (interval_ul)
		ulclientApps.Start( Seconds (1.0));
	//lteHelper->EnableTraces ();
	lteHelper->EnableRlcTraces ();
	
	Ptr <FlowMonitor> flowmon;
	FlowMonitorHelper fmHelper;
	flowmon = fmHelper.Install (ueNodes);
	flowmon = fmHelper.Install (remoteHostContainer);
	Simulator::Schedule(Seconds(3), &ThroughputMonitor, &fmHelper, flowmon); 

	Simulator::Stop(Seconds(simTime));
	config.ConfigureAttributes ();

	char buff[100];
	for (uint8_t i=0; i<ueNodes.GetN (); ++i) {
		sprintf(buff, "pcap_%d.pcap", i);
		std::string buffAsStdStr = buff;
		p2pv[i]->EnablePcap(buffAsStdStr, remoteHostContainer.Get(i)->GetDevice(1), false, true);
	}

	Simulator::Run();
	Simulator::Destroy();
	return 0;
}

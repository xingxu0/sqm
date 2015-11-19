/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

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

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("LTEExample");

int
main (int argc, char *argv[])
{
	
	uint16_t numberOfNodes = 20;
	double simTime = 5;
	double distance = 500.0;
	double interPacketInterval = 0.0000000000001;
	
	CommandLine cmd;
  cmd.AddValue("numberOfNodes", "Number of eNodeBs + UE pairs", numberOfNodes);
  cmd.AddValue("simTime", "Total duration of the simulation [s])", simTime);
  cmd.AddValue("distance", "Distance between eNBs [m]", distance);
  cmd.AddValue("interPacketInterval", "Inter packet interval [ms])", interPacketInterval);
  cmd.Parse(argc, argv);
  std::cout<<"distance"<<distance<<std::endl;
  std::cout<<"interval"<<interPacketInterval<<std::endl;
	
	Ptr<LteHelper> lteHelper = CreateObject<LteHelper> ();
	  lteHelper->SetAttribute ("PathlossModel", StringValue ("ns3::FriisPropagationLossModel"));
	Ptr<PointToPointEpcHelper> epcHelper = CreateObject<PointToPointEpcHelper> ();
	lteHelper->SetEpcHelper (epcHelper);
	
	  ConfigStore inputConfig;
  inputConfig.ConfigureDefaults();
    cmd.Parse(argc, argv);
	
	Ptr<Node> pgw = epcHelper->GetPgwNode ();

	// Create a single RemoteHost
	NodeContainer remoteHostContainer;
	remoteHostContainer.Create (1);
	Ptr<Node> remoteHost = remoteHostContainer.Get (0);
	InternetStackHelper internet;
	internet.Install (remoteHostContainer);

	// Create the internet
	PointToPointHelper p2ph;
	p2ph.SetDeviceAttribute ("DataRate", DataRateValue (DataRate ("100Gb/s")));
	p2ph.SetDeviceAttribute ("Mtu", UintegerValue (1500));
	p2ph.SetChannelAttribute ("Delay", TimeValue (Seconds (interPacketInterval)));
	NetDeviceContainer internetDevices = p2ph.Install (pgw, remoteHost);
	Ipv4AddressHelper ipv4h;
	ipv4h.SetBase ("1.0.0.0", "255.0.0.0");
	Ipv4InterfaceContainer internetIpIfaces = ipv4h.Assign (internetDevices);
	// interface 0 is localhost, 1 is 15the p2p device
	//Ipv4Address remoteHostAddr = internetIpIfaces.GetAddress (1);
	internetIpIfaces.GetAddress (1);
	
	Ipv4StaticRoutingHelper ipv4RoutingHelper;
	Ptr<Ipv4StaticRouting> remoteHostStaticRouting = ipv4RoutingHelper.GetStaticRouting (remoteHost->GetObject<Ipv4> ());
	remoteHostStaticRouting->AddNetworkRouteTo (Ipv4Address ("7.0.0.0"), Ipv4Mask ("255.0.0.0"), 1);
	
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
  positionAlloc->Add (Vector(0, 0, 0));
  for (uint16_t i = 0; i < numberOfNodes + 1; i++)
    {
      positionAlloc->Add (Vector(distance, 0, 0));
      //positionAlloc->Add (Vector(distance, 0, 0));
    }
  MobilityHelper mobility;
  mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
  mobility.SetPositionAllocator(positionAlloc);
  mobility.Install(enbNodes);
  mobility.Install(ueNodes);
  
    NetDeviceContainer enbLteDevs = lteHelper->InstallEnbDevice (enbNodes);
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
    
  // Attach one UE per eNodeB

  for (uint16_t i = 0; i < numberOfNodes; i++)
      {
        //lteHelper->Attach (ueLteDevs.Get(i), enbLteDevs.Get(i));
	lteHelper->Attach (ueLteDevs.Get(i));//, enbLteDevs.Get(i));
        // side effect: the default EPS bearer will be activated
      }  
    
// bearer      
for (uint16_t u = 0; u < ueNodes.GetN (); u++)
      {
      Ptr<NetDevice> ueDevice = ueLteDevs.Get (u);

      GbrQosInformation qos;
      qos.gbrDl = 132;  // bit/s, considering IP, UDP, RLC, PDCP header size
      qos.gbrUl = 132;
      qos.mbrDl = qos.gbrDl;
      qos.mbrUl = qos.gbrUl;

enum EpsBearer::Qci q;
	if (u  == 0) q = EpsBearer::NGBR_VOICE_VIDEO_GAMING;
	else if (u==1) q=EpsBearer::NGBR_VIDEO_TCP_PREMIUM; 
	else q = EpsBearer::NGBR_VIDEO_TCP_DEFAULT;
      EpsBearer bearer (q);

      /*
      if (u  == 0) bearer.arp.priorityLevel = 1;
      else bearer.arp.priorityLevel = 15;
      
      
      if (u==0)
      {
	      NS_LOG_UNCOND("higher priority");
      bearer.arp.preemptionCapability = true;
      bearer.arp.preemptionVulnerability = false;
      }
      else {
	      NS_LOG_UNCOND("lower priority");
	      bearer.arp.preemptionCapability = false;
      bearer.arp.preemptionVulnerability = true;
}*/

      uint8_t bid = lteHelper->ActivateDedicatedEpsBearer (ueDevice, bearer, EpcTft::Default ());
      std::cout<<u<<"'s bearer id: "<<(int)bid<<std::endl;
      }
  
  
		
  // Install and start applications on UEs and remote host
  uint16_t dlPort = 1234;
  uint16_t ulPort = 2000;
  uint16_t otherPort = 3000;
  ApplicationContainer clientApps;
  ApplicationContainer serverApps;
    for (uint32_t u = 0; u < ueNodes.GetN (); ++u)
    {
      ++ulPort;
      ++otherPort;
      PacketSinkHelper dlPacketSinkHelper ("ns3::TcpSocketFactory", InetSocketAddress (Ipv4Address::GetAny (), dlPort));
      //PacketSinkHelper ulPacketSinkHelper ("ns3::UdpSocketFactory", InetSocketAddress (Ipv4Address::GetAny (), ulPort));
      //PacketSinkHelper packetSinkHelper ("ns3::UdpSocketFactory", InetSocketAddress (Ipv4Address::GetAny (), otherPort));
      serverApps.Add (dlPacketSinkHelper.Install (ueNodes.Get(u)));
      //serverApps.Add (ulPacketSinkHelper.Install (remoteHost));
      //serverApps.Add (packetSinkHelper.Install (ueNodes.Get(u)));

      //TcpClientHelper dlClient (ueIpIface.GetAddress (u), dlPort);

        BulkSendHelper dlClient ("ns3::TcpSocketFactory",InetSocketAddress (ueIpIface.GetAddress (u), dlPort));
      //dlClient.SetAttribute ("Interval", TimeValue (MilliSeconds(1)));
      //dlClient.SetAttribute ("MaxPackets", UintegerValue(1000000000));
      dlClient.SetAttribute ("MaxBytes", UintegerValue (0));

      // sender infor, check later.
      /*
      UdpClientHelper ulClient (remoteHostAddr, ulPort);
      ulClient.SetAttribute ("Interval", TimeValue (MilliSeconds(interPacketInterval)));
      ulClient.SetAttribute ("MaxPackets", UintegerValue(1000000));

      UdpClientHelper client (ueIpIface.GetAddress (u), otherPort);
      client.SetAttribute ("Interval", TimeValue (MilliSeconds(interPacketInterval)));
      client.SetAttribute ("MaxPackets", UintegerValue(1000000));
      */
      clientApps.Add(dlClient.Install(remoteHost));
/*
      clientApps.Add (dlClient.Install (remoteHost));
      clientApps.Add (ulClient.Install (ueNodes.Get(u)));
      if (u+1 < ueNodes.GetN ())
        {
          clientApps.Add (client.Install (ueNodes.Get(u+1)));
        }
      else
        {
          clientApps.Add (client.Install (ueNodes.Get(0)));
        }*/
    }
    
      serverApps.Start (Seconds (1.0));
  clientApps.Start (Seconds (1.0));
  lteHelper->EnableTraces ();
  // Uncomment to enable PCAP tracing
  p2ph.EnablePcapAll("lena-epc-first");

  Simulator::Stop(Seconds(simTime));
  Simulator::Run();

  /*GtkConfigStore config;
  config.ConfigureAttributes();*/

  Simulator::Destroy();
  return 0;
  
  /*
	
	uint16_t dlPort = 1234;
	PacketSinkHelper packetSinkHelper ("ns3::UdpSocketFactory",
					InetSocketAddress (Ipv4Address::GetAny (), dlPort));
	ApplicationContainer serverApps = packetSinkHelper.Install (ueNodes);
	serverApps.Start (Seconds (0.01));

	// assign IP address to UEs
	for (uint32_t u = 0; u < ueNodes.GetN (); ++u)
	{
		Ptr<Node> ue = ueNodes.Get (u);
		Ptr<NetDevice> ueLteDevice = ueLteDevs.Get (u);
		Ipv4InterfaceContainer ueIpIface = epcHelper->AssignUeIpv4Address (NetDeviceContainer (ueLteDevice));
		// set the default gateway for the UE
		Ptr<Ipv4StaticRouting> ueStaticRouting = ipv4RoutingHelper.GetStaticRouting (ue->GetObject<Ipv4> ());
		ueStaticRouting->SetDefaultRoute (epcHelper->GetUeDefaultGatewayAddress (), 1);
		
		UdpClientHelper client (ueIpIface.GetAddress (0), dlPort);
		ApplicationContainer clientApps = client.Install (remoteHost);
		clientApps.Start (Seconds (0.01));
	}	
	*/
	/*
	Ptr<EpcTft> tft = Create<EpcTft> ();
	EpcTft::PacketFilter pf;
	pf.localPortStart = 1234;
	pf.localPortEnd = 1234;
	tft->Add (pf);
	lteHelper->ActivateDedicatedEpsBearer (ueLteDevs, EpsBearer (EpsBearer::NGBR_VIDEO_TCP_DEFAULT), tft);
	*/
	
	
	//UdpClientHelper client (ueIpIface.GetAddress (0), dlPort);
	//ApplicationContainer clientApps = client.Install (remoteHost);
	//clientApps.Start (Seconds (0.01));
	/*
	MobilityHelper mobility;
	mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
	mobility.Install (enbNodes);
	mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
	mobility.Install (ueNodes);

	NetDeviceContainer enbDevs;
	enbDevs = lteHelper->InstallEnbDevice (enbNodes);

	NetDeviceContainer ueDevs;
	ueDevs = lteHelper->InstallUeDevice (ueNodes);

	//lteHelper->Attach (ueDevs, enbDevs.Get (0)); // manual attachment
	lteHelper->Attach (ueDevs); // automatic attachment

	enum EpsBearer::Qci q = EpsBearer::GBR_CONV_VOICE;
	EpsBearer bearer (q);
	lteHelper->ActivateDataRadioBearer (ueDevs, bearer);

	Simulator::Stop (Seconds (0.005));
	
	lteHelper->EnablePhyTraces ();
	lteHelper->EnableMacTraces ();
	lteHelper->EnableRlcTraces ();
	lteHelper->EnablePdcpTraces ();

	Simulator::Run ();

	Simulator::Destroy ();
	return 0;
	*/
}

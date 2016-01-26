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
#include <vector>

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("LTEExample");

int
main (int argc, char *argv[])
{
	
	uint16_t numberOfNodes = 10;
	double simTime = 60;
	double distance = 15000.0;
	double p_distance = 15000.0;
	double interPacketInterval = 0.01;
	std::string dataRate = "100";
	std::string slow_dataRate = "0.1";
	slow_dataRate = "100";
	int gold_user = 0;
	int silver_user = 0;
	
	CommandLine cmd;
  cmd.AddValue("nodes", "Number of eNodeBs + UE pairs", numberOfNodes);
  cmd.AddValue("simTime", "Total duration of the simulation [s])", simTime);
  cmd.AddValue("distance", "Distance between eNBs [m]", distance);
  cmd.AddValue("premium_distance", "Distance between eNBs [m]", p_distance);
  cmd.AddValue("dataRate", "data rate [Gb/s])", dataRate);
  cmd.AddValue("slowdataRate", "data rate [Gb/s])", slow_dataRate);
  //cmd.AddValue("interPacketInterval", "Inter packet interval [ms])", interPacketInterval);
  cmd.AddValue("goldUser", "gu", gold_user);
  cmd.AddValue("silverUser", "gu", silver_user);
  cmd.Parse(argc, argv);
  std::cout<<"distance"<<distance<<std::endl;
  std::cout<<"interval"<<interPacketInterval<<std::endl;
  std::cout<<"dataRate"<<dataRate<<std::endl;
	
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
	remoteHostContainer.Create (numberOfNodes);
	//
	InternetStackHelper internet;
	internet.Install (remoteHostContainer);

	std::vector<PointToPointHelper*> p2pv;
	// Create the internet
	
	
	Ipv4StaticRoutingHelper ipv4RoutingHelper;
	for (uint16_t i = 0; i < numberOfNodes; i++) {
		PointToPointHelper* p2ph = new PointToPointHelper();
		//if (i<numberOfNodes / 2)
		if (i<1)
			p2ph->SetDeviceAttribute ("DataRate", DataRateValue (DataRate (dataRate + "Mb/s")));
		else
			p2ph->SetDeviceAttribute ("DataRate", DataRateValue (DataRate (slow_dataRate + "Mb/s")));
		p2ph->SetDeviceAttribute ("Mtu", UintegerValue (1500));
		p2ph->SetChannelAttribute ("Delay", TimeValue (Seconds (interPacketInterval)));
		
		Ptr<Node> remoteHost = remoteHostContainer.Get (i);
		NetDeviceContainer internetDevices = p2ph->Install (pgw, remoteHost);
		Ipv4AddressHelper ipv4h;
		char buf[512];
        sprintf(buf,"1.0.%d.0", i);
		ipv4h.SetBase (buf, "255.255.255.0");
		Ipv4InterfaceContainer internetIpIfaces = ipv4h.Assign (internetDevices);
	// interface 0 is localhost, 1 is 15the p2p device
	//Ipv4Address remoteHostAddr = internetIpIfaces.GetAddress (1);
		internetIpIfaces.GetAddress (1);
		Ptr<Ipv4StaticRouting> remoteHostStaticRouting = ipv4RoutingHelper.GetStaticRouting (remoteHost->GetObject<Ipv4> ());
		remoteHostStaticRouting->AddNetworkRouteTo (Ipv4Address ("7.0.0.0"), Ipv4Mask ("255.0.0.0"), 1);
		
		p2pv.push_back(p2ph);
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
  positionAlloc->Add (Vector(0, 0, 0));
  
  for (uint16_t i = 0; i < numberOfNodes + 1; i++)
    {
	    /*
      if (i==1)
		positionAlloc->Add (Vector(distance/2.0, 0, 0));
	else*/
	    
      //if (i < gold_user)
     if (i < 1) 		
	positionAlloc->Add (Vector(p_distance, 0, 0));
      else
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
      if (u < gold_user) q = EpsBearer::NGBR_VOICE_VIDEO_GAMING;
      else if (u < gold_user + silver_user) q=EpsBearer::NGBR_VIDEO_TCP_PREMIUM; 
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
  uint16_t dlPort = 33333;
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
	  Ptr<Node> remoteHost = remoteHostContainer.Get (u);
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
  
  char buff[100];
  
  std::cout<<"PCAP"<<std::endl;
  for (uint8_t i=0; i<ueNodes.GetN (); ++i) {
	//sprintf(buff, "trace_nonsharing_d%d_gu%d_su%d_r%sGb_id%d.pcap", (int)distance, gold_user, silver_user, dataRate.c_str(), i);
	sprintf(buff, "trace_nonsharing_%d.pcap", i);
	std::string buffAsStdStr = buff;
	std::cout<<remoteHostContainer.Get(i)->GetNDevices()<<std::endl;
	p2pv[i]->EnablePcap(buffAsStdStr, remoteHostContainer.Get(i)->GetDevice(1), false, true);
  }
  
  //sprintf(buff, "trace_nonsharing_d%d_gu%d_su%d_r%sGb_id%d", (int)distance, gold_user, silver_user, dataRate.c_str(), 0);
  //std::string buffAsStdStr = buff;
  //std::cout<<remoteHostContainer.Get(0)->GetNDevices<<std::endl;
  //p2pv[0]->EnablePcap(buffAsStdStr, remoteHostContainer.Get(0)->GetDevice(0));//, remoteHostContainer.Get(i));
  

  Simulator::Stop(Seconds(simTime));
  Simulator::Run();

  /*GtkConfigStore config;
  config.ConfigureAttributes();*/

  Simulator::Destroy();
  return 0;
}

// ./waf --run "scratch/hex --ns3::ConfigStore::Mode=Save --ns3::ConfigStore::Filename=config.txt"; gnuplot -p enbs.txt ues.txt my_plot_script; cp myplot.png ~/Dropbox/myplot3.png




/* 12 users, 3 groups, A, B, C
 * group A & B: infinite traffic to receive
 * group C: controlled demand
 * group A will be configured as premium
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
#include "ns3/data-rate.h"
#include "ns3/point-to-point-net-device.h"
#include "ns3/radio-environment-map-helper.h"
#include "../src/lte/model/weight-table.h"
#include <vector>

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("LTEExample");

void modify_requirement(int n, std::vector<NetDeviceContainer> &ndc)
{
	DataRate x("0.00001Mb/s");
	for (unsigned i = 0; i<ndc.size(); ++i) {
		if (i%2==0) continue;
		Ptr<PointToPointNetDevice> p2pdev1 = StaticCast<PointToPointNetDevice> (ndc[i].Get(0));
		Ptr<PointToPointNetDevice> p2pdev2 = StaticCast<PointToPointNetDevice> (ndc[i].Get(1));
		p2pdev1->SetDataRate(x);
		p2pdev2->SetDataRate(x);
	}
	//Config::Set("/NodeList/0/DeviceList/0/$ns3::PointToPointNetDevice/DataRate", StringValue("0.1Mb/s") );
	//Config::Set("/NodeList/1/DeviceList/1/$ns3::PointToPointNetDevice/DataRate", StringValue("0.1Mb/s") );

}

void 
PrintGnuplottableUeListToFile (std::string filename)
{
	  std::ofstream outFile;
	    outFile.open (filename.c_str (), std::ios_base::out | std::ios_base::trunc);
	      if (!outFile.is_open ())
		          {
				        NS_LOG_ERROR ("Can't open file " << filename);
					      return;
					          }
	        for (NodeList::Iterator it = NodeList::Begin (); it != NodeList::End (); ++it)
			    {
				          Ptr<Node> node = *it;
					        int nDevs = node->GetNDevices ();
						      for (int j = 0; j < nDevs; j++)
							              {
									                Ptr<LteUeNetDevice> uedev = node->GetDevice (j)->GetObject <LteUeNetDevice> ();
											          if (uedev)
													              {
															                    Vector pos = node->GetObject<MobilityModel> ()->GetPosition ();
																	                  outFile << "set label \"" << uedev->GetImsi ()
																				                        << "\" at "<< pos.x << "," << pos.y << " left font \"Helvetica,4\" textcolor rgb \"grey\" front point pt 1 ps 0.3 lc rgb \"grey\" offset 0,0"
																							                      << std::endl;
																			              }
												          }
						          }
}

void 
PrintGnuplottableEnbListToFile (std::string filename)
{
	  std::ofstream outFile;
	    outFile.open (filename.c_str (), std::ios_base::out | std::ios_base::trunc);
	      if (!outFile.is_open ())
		          {
				        NS_LOG_ERROR ("Can't open file " << filename);
					      return;
					          }
	        for (NodeList::Iterator it = NodeList::Begin (); it != NodeList::End (); ++it)
			    {
				          Ptr<Node> node = *it;
					        int nDevs = node->GetNDevices ();
						      for (int j = 0; j < nDevs; j++)
							              {
									                Ptr<LteEnbNetDevice> enbdev = node->GetDevice (j)->GetObject <LteEnbNetDevice> ();
											          if (enbdev)
													              {
															                    Vector pos = node->GetObject<MobilityModel> ()->GetPosition ();
																	                  outFile << "set label \"" << enbdev->GetCellId ()
																				                        << "\" at "<< pos.x << "," << pos.y
																							                      << " left font \"Helvetica,4\" textcolor rgb \"white\" front  point pt 2 ps 0.3 lc rgb \"white\" offset 0,0"
																									                            << std::endl;
																			              }
												          }
						          }
}

int
main (int argc, char *argv[])
{

  imsi_id = new std::map <uint64_t, uint16_t>();
  rnti_imsi = new std::map <uint16_t, uint64_t>();
  id_weight = new std::map<uint16_t, float>();
  rnti_mcs = new std::map <uint16_t, uint8_t>();
 rnti_rate = new std::map<uint16_t, double>();

 uint16_t numberOfNodes = 12;
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
    ConfigStore config;
      config.ConfigureDefaults ();
	
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
	NetDeviceContainer internetDevices;
	std::vector<NetDeviceContainer> ndc;
	for (uint16_t i = 0; i < numberOfNodes; i++) {
		PointToPointHelper* p2ph = new PointToPointHelper();
		//if (i<numberOfNodes / 2)
		if (1)//(i<8)
			p2ph->SetDeviceAttribute ("DataRate", DataRateValue (DataRate (dataRate + "Mb/s")));
		else
			p2ph->SetDeviceAttribute ("DataRate", DataRateValue (DataRate (slow_dataRate + "Mb/s")));
		p2ph->SetDeviceAttribute ("Mtu", UintegerValue (1500));
		p2ph->SetChannelAttribute ("Delay", TimeValue (Seconds (interPacketInterval)));
		
		Ptr<Node> remoteHost = remoteHostContainer.Get (i);
		internetDevices = p2ph->Install (pgw, remoteHost);
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
		ndc.push_back(internetDevices);
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
  enbNodes.Create(12);
  ueNodes.Create(numberOfNodes);
  
    // Install Mobility Model
  Ptr<ListPositionAllocator> positionAlloc = CreateObject<ListPositionAllocator> ();
 /* 
     positionAlloc->Add (Vector(8000, 0, 0));
    positionAlloc->Add (Vector(8000,0, 0));
  positionAlloc->Add (Vector(8000, 0, 0));
positionAlloc->Add (Vector(0, 0, 0));
  positionAlloc->Add (Vector(0, 0, 0));
  positionAlloc->Add (Vector(0, 0, 0));
  */
  



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
    mobility.Install(enbNodes);
mobility.SetPositionAllocator(positionAlloc);

  mobility.Install(ueNodes);
  
  Ptr<LteHexGridEnbTopologyHelper> lteHexGridEnbTopologyHelper = CreateObject<LteHexGridEnbTopologyHelper> ();
  lteHexGridEnbTopologyHelper->SetLteHelper (lteHelper);
  double interSiteDistance = 8000;
  lteHexGridEnbTopologyHelper->SetAttribute ("InterSiteDistance", DoubleValue (interSiteDistance));
  lteHexGridEnbTopologyHelper->SetAttribute ("MinX", DoubleValue (interSiteDistance/2));
  lteHexGridEnbTopologyHelper->SetAttribute ("GridWidth", UintegerValue (1));
  //Config::SetDefault ("ns3::LteEnbPhy::TxPower", DoubleValue (macroEnbTxPowerDbm));
  lteHelper->SetEnbAntennaModelType ("ns3::ParabolicAntennaModel");
  lteHelper->SetEnbAntennaModelAttribute ("Beamwidth",   DoubleValue (70));
  lteHelper->SetEnbAntennaModelAttribute ("MaxAttenuation",     DoubleValue (20.0));
  //lteHelper->SetEnbDeviceAttribute ("DlEarfcn", UintegerValue (macroEnbDlEarfcn));
  //lteHelper->SetEnbDeviceAttribute ("UlEarfcn", UintegerValue (macroEnbDlEarfcn + 18000));
  lteHelper->SetEnbDeviceAttribute ("DlBandwidth", UintegerValue (25));
  lteHelper->SetEnbDeviceAttribute ("UlBandwidth", UintegerValue (25));
  NetDeviceContainer enbLteDevs = lteHexGridEnbTopologyHelper->SetPositionAndInstallEnbDevice (enbNodes);
  
    //NetDeviceContainer enbLteDevs = lteHelper->InstallEnbDevice (enbNodes);
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

	  std::cout<<"Print out IMSI"<<std::endl;
for (uint16_t u = 0; u < ueNodes.GetN (); u++) {
	uint64_t imsi = ueLteDevs.Get (u)->GetObject<LteUeNetDevice> ()->GetImsi ();
	std::cout<<imsi<<std::endl;
	(*imsi_id)[imsi] = u;
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
	gold_user = 0;
	silver_user = 0;
      if (u < gold_user) (*id_weight)[u] = 4;//q = EpsBearer::NGBR_VOICE_VIDEO_GAMING;
      else if (u < gold_user + silver_user) (*id_weight)[u] = 2;//q=EpsBearer::NGBR_VIDEO_TCP_PREMIUM; 
      else (*id_weight)[u] = 1;
	      
	      
     q = EpsBearer::NGBR_VIDEO_TCP_DEFAULT;
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
  
  
  //sprintf(buff, "trace_nonsharing_d%d_gu%d_su%d_r%sGb_id%d", (int)distance, gold_user, silver_user, dataRate.c_str(), 0);
  //std::string buffAsStdStr = buff;
  //std::cout<<remoteHostContainer.Get(0)->GetNDevices<<std::endl;
  //p2pv[0]->EnablePcap(buffAsStdStr, remoteHostContainer.Get(0)->GetDevice(0));//, remoteHostContainer.Get(i));
  
  //Simulator::Schedule(Seconds(10), &modify_weight, numberOfNodes);
  Simulator::Schedule(Seconds(8), &modify_requirement, numberOfNodes, ndc);
  
  Simulator::Stop(Seconds(simTime));

/*
        PrintGnuplottableEnbListToFile ("enbs.txt");
	      PrintGnuplottableUeListToFile ("ues.txt");
  Ptr<RadioEnvironmentMapHelper> remHelper = CreateObject<RadioEnvironmentMapHelper> ();
  remHelper->SetAttribute ("ChannelPath", StringValue ("/ChannelList/12"));
  remHelper->SetAttribute ("OutputFile", StringValue ("rem.out"));
  remHelper->SetAttribute ("XMin", DoubleValue (-15000));
  remHelper->SetAttribute ("XMax", DoubleValue (15000));
  remHelper->SetAttribute ("XRes", UintegerValue (100));
  remHelper->SetAttribute ("YMin", DoubleValue (-15000));
  remHelper->SetAttribute ("YMax", DoubleValue (15000.0));
  remHelper->SetAttribute ("YRes", UintegerValue (100));
  remHelper->SetAttribute ("Z", DoubleValue (0.0));
  remHelper->SetAttribute ("UseDataChannel", BooleanValue (false));
  remHelper->SetAttribute ("RbId", IntegerValue (-1));
  remHelper->Install ();*/
  
  config.ConfigureAttributes ();

  char buff[100];
  
  std::cout<<"PCAP"<<std::endl;
  for (uint8_t i=0; i<ueNodes.GetN (); ++i) {
	//sprintf(buff, "trace_nonsharing_d%d_gu%d_su%d_r%sGb_id%d.pcap", (int)distance, gold_user, silver_user, dataRate.c_str(), i);
	sprintf(buff, "dynamic_weight_%d.pcap", i);
	std::string buffAsStdStr = buff;
	std::cout<<remoteHostContainer.Get(i)->GetNDevices()<<std::endl;
	p2pv[i]->EnablePcap(buffAsStdStr, remoteHostContainer.Get(i)->GetDevice(1), false, true);
  }

  Simulator::Run();

  /*GtkConfigStore config;
  config.ConfigureAttributes();*/

  Simulator::Destroy();
  return 0;
}

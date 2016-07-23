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

Ptr<LteAmc> amc;
uint16_t n1 = 10;
uint16_t n2 = 4;
uint16_t n3 = 4;
uint16_t numberOfNodes = 18;
int maintain_thr = 200000; // in terms of B/s
int rate_maintain_users = 0;
float interval_mcs = 1;
float interval_requirement = 1;


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
	
	for (std::map<uint16_t, uint64_t>::iterator it=rnti_am_mode_bytes_adjustment->begin(); it!=rnti_am_mode_bytes_adjustment->end(); it++) {
		if (rnti_imsi->find(it->first) != rnti_imsi->end())
			std::cout<<(*rnti_imsi)[it->first]<<" can send more bytes: "<<it->second<<std::endl;
		it->second = 0;
	}
	Simulator::Schedule(Seconds(1),&ThroughputMonitor, fmhelper, flowMon);
}

void NotifyConnectionEstablishedEnb (std::string context,
                                uint64_t imsi,
                                uint16_t cellid,
                                uint16_t rnti)
{
  std::cout << Simulator::Now ().GetSeconds () << " " << context
            << " eNB CellId " << cellid
            << ": successful connection of UE with IMSI " << imsi
            << " RNTI " << rnti;
  uint16_t my_rnti = cellid*1000+rnti;
  (*rnti_imsi)[my_rnti] = imsi;
  (*rnti_rate)[my_rnti] = 0;
  (*rnti_mcs)[my_rnti] = 0;
  (*rnti_prbs)[my_rnti] = 0;
  
  (*rnti_mcs)[my_rnti] = 0;
  std::cout << " weight " << (*id_weight)[(*imsi_id)[(*rnti_imsi)[my_rnti]]]<<std::endl;
}

template<typename KK, typename VV>
KK get_key_from_value(VV v, std::map<KK,VV> *m){
	typename std::map<KK,VV>::iterator it; 
	for (it=m->begin(); it!=m->end(); it++){
		if (it->second == v)
			return it->first;
	}
	return (KK)-1;
}

void clear_prb() {
	for (uint16_t i=0; i<numberOfNodes; ++i){
		uint64_t imsi = get_key_from_value(i, imsi_id);
		uint16_t rnti = get_key_from_value(imsi, rnti_imsi);
		(*rnti_prbs_previous)[rnti] = (*rnti_prbs)[rnti];
		(*rnti_prbs)[rnti] = 0;
	}
}

void clear_mcs() {
	for (uint16_t i=0; i<numberOfNodes; ++i){
		uint64_t imsi = get_key_from_value(i, imsi_id);
		uint16_t rnti = get_key_from_value(imsi, rnti_imsi);
		//(*rnti_prbs)[rnti] = 0;
		(*rnti_mcs)[rnti] = 0;
		(*rnti_mcs_count)[rnti] = 0;
		(*rnti_mcs_selected)[rnti] = 0;
		(*rnti_mcs_count_selected)[rnti] = 0;
		(*rnti_mcs_max)[rnti] = 0;
		for (uint8_t j=0; j<29; ++j)
			(*rnti_mcs_log)[rnti].mcs[j] = 0;
	}
}

void update_w() {
	int total_prb = 0;
	int total_prb_normal_users = 0;
	int n = 0;
	// start from 1 to exclude premium user
	for (uint16_t i=0; i<n1; ++i) {
		uint64_t imsi = get_key_from_value(i, imsi_id);
		uint16_t rnti = get_key_from_value(imsi, rnti_imsi);
		total_prb += (*rnti_prbs_previous)[rnti];
		if (i >= rate_maintain_users)
			total_prb_normal_users += (*rnti_prbs_previous)[rnti];
		if ((*rnti_prbs_previous)[rnti] > 0) n += 1;
		std::cout<<i<<":"<<(int)(*rnti_prbs_previous)[rnti]<<",";
	}
//std::cout<<std::endl;
	
	float fair_share = total_prb_normal_users*1.0/(n-rate_maintain_users);
	int light_user_prb = 0;
	int light_user = 0;
	for (uint16_t i=0; i<n1; ++i){
		if (i<rate_maintain_users) // we don't count premium users as light user
			continue;
		uint64_t imsi = get_key_from_value(i, imsi_id);
		uint16_t rnti = get_key_from_value(imsi, rnti_imsi);
		if ((*rnti_prbs_previous)[rnti] < fair_share)
		{
			light_user_prb += (*rnti_prbs_previous)[rnti];
			light_user += 1;
		}
	}
	
	int heavy_user_prb = total_prb - light_user_prb;
	int heavy_user = n1 - light_user;
	// total / (n + w - 1) = maintain_thr
	
	//float new_w = (maintain_thr - maintain_thr*heavy_user)*1.0/(maintain_thr - heavy_user_prb);
	std::vector<int> prbs;
	std::vector<int> estimated;
	float new_maintain_thr = 0;
	for (uint16_t i=0; i<rate_maintain_users; ++i){
		uint64_t imsi = get_key_from_value(i, imsi_id);
		uint16_t rnti = get_key_from_value(imsi, rnti_imsi);
		
		float mcs_value = (int)(*rnti_mcs_count_selected)[rnti] == 0 ? -1 : (*rnti_mcs_selected)[rnti]*1.0/(*rnti_mcs_count_selected)[rnti];
		//if (mcs_value > 28 || mcs_value < 0) {
		if (mcs_value == 0 || mcs_value<16 || mcs_value>712) {
			std::cout<<i<<" s mcs value issue"<<mcs_value<<" "<<(int) (*rnti_mcs)[rnti]<<":"<<(*rnti_mcs_count)[rnti]<<"   ";
			mcs_value = 712;
		}
		float prb =  4.0*interval_requirement*maintain_thr / mcs_value; // 2 is an arbitrary number
		prbs.push_back(prb);
		estimated.push_back(mcs_value);
		new_maintain_thr += prb;
	}
	std::cout<<std::endl;
	int new_heavy_user = heavy_user - rate_maintain_users + 1;
	float new_w = (new_maintain_thr - new_maintain_thr*new_heavy_user)*1.0/(new_maintain_thr - heavy_user_prb);
	
	//if (new_w > 1) (*id_weight)[0] = new_w;
	//if (each_w > 1)
	//	for (uint16_t i=0; i<rate_maintain_users; ++i) (*id_weight)[i] = each_w;
	std::cout<<"new rate maintain user's w"<<std::endl;
	for (uint16_t i=0; i<rate_maintain_users; ++i) {
		uint64_t imsi = get_key_from_value(i, imsi_id);
		uint16_t rnti = get_key_from_value(imsi, rnti_imsi);
		float w = new_w*prbs[i]/new_maintain_thr;
		(*id_weight)[i] = w > 1 ? w : 1;
		std::cout<<i<<", mcs:"<<(int)(*rnti_mcs)[rnti]
			<<", count:"<<(int)(*rnti_mcs_count)[rnti]
			<<"("<< int(round(((*rnti_mcs_count)[rnti] == 0 ? -1 : (*rnti_mcs)[rnti]*1.0/(*rnti_mcs_count)[rnti])))
			<<") selected mcs:"<<(int)(*rnti_mcs_selected)[rnti]
			<<", selected count:"<<(int)(*rnti_mcs_count_selected)[rnti]
			<<"("<< int(round(((int)(*rnti_mcs_count_selected)[rnti] == 0 ? -1 : (*rnti_mcs_selected)[rnti]*1.0/(*rnti_mcs_count_selected)[rnti])))
			<<"), prb:"<<prbs[i]
			<<", w:"<<w
			<<", estimated:"<<(int)estimated[i]<<std::endl;
	}
	
	//std::cout<<"new weight:"<<new_w<<" total_prb:"<<(int)total_prb<<" total_prb_normal_users:"<<(int)total_prb_normal_users<<" light_user:"<<(int)light_user<<" light_user_prb:"<<(int)light_user_prb<<" heavy_user:"<<(int)heavy_user<<" heavy user prb:"<<(int)heavy_user_prb<<" fair share:"<<fair_share<<std::endl;
	std::cout<<"new weight:"<<new_w<<"total_prb:"<<(int)total_prb<<" total_prb_normal_users:"<<(int)total_prb_normal_users<<" light_user:"<<(int)light_user<<" light_user_prb:"<<(int)light_user_prb<<" heavy_user:"<<(int)heavy_user<<"("<<(int)new_heavy_user<<") heavy user prb:"<<(int)heavy_user_prb<<" fair share:"<<fair_share<<std::endl;	
}

void dynamic_maintain() {
	for (std::map<uint64_t, uint16_t>::iterator it=imsi_id->begin(); it!=imsi_id->end(); it++) {
		std::cout<<" "<<it->first<<":"<<it->second<<", ";
	}
	std::cout<<std::endl;

	for (uint16_t i=0; i<n1; ++i){
		std::cout<<(int)i<<": ";
		uint64_t imsi = get_key_from_value(i, imsi_id);
		uint16_t rnti = get_key_from_value(imsi, rnti_imsi);
		std::cout<<"imsi:"<<imsi<<" rnti:"<<rnti<<"  ";
		std::cout<<(int)(*rnti_mcs)[rnti]<<" "<<(*rnti_rate)[rnti]<<" "<<(*rnti_prbs)[rnti]<<std::endl;
	}
	update_w();
	clear_mcs();
}

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
PrintGnuplottableToFile ()
{
	std::ofstream outFile;
	outFile.open ("ues.out", std::ios_base::out | std::ios_base::trunc);
	if (!outFile.is_open ())
	{
		NS_LOG_ERROR ("Can't open file " << "ues.out");
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
	outFile.close();
	//std::ofstream outFile;
	outFile.open ("enbs.out", std::ios_base::out | std::ios_base::trunc);
	if (!outFile.is_open ())
	{
		NS_LOG_ERROR ("Can't open file " << "enbs.out");
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

void generate_x_y(int d, int &x, int &y) {
	int degree = rand()%360 + 1;
	x = (int)(d*1.0*sin (degree*PI/180));
	y = (int)(d*1.0*cos (degree*PI/180));
}

int
main (int argc, char *argv[])
{
	LogLevel logLevel = (LogLevel)(LOG_LEVEL_INFO|LOG_PREFIX_TIME);
	LogComponentEnable ("PfFfMacScheduler", logLevel);
	
	init();
	amc = CreateObject <LteAmc> ();
	srand (0);
	double simTime = 120;
	double distance = 1000.0;
	double distance2 = 1000.0;
	double interPacketInterval = 0.01;
	std::string dataRate = "100";
	std::string slow_dataRate = "0.2";
	int gold_user = 0;
	int silver_user = 0;
	bool plot_sinr = false;
	double interSiteDistance = 2000;
	int interferer = 1;
	int bs = 3;
	int weight = 4;
	int ack = 1;
	bool udp = false;
	bool dynamic = false;
	bool random_location = false;
	bool fading = false;
	
	CommandLine cmd;
	cmd.AddValue("nodes", "Number of eNodeBs + UE pairs", numberOfNodes);
	cmd.AddValue("simTime", "Total duration of the simulation [s])", simTime);
	cmd.AddValue("distance", "Distance between eNBs [m]", distance);
	cmd.AddValue("distance2", "Distance between eNBs [m]", distance2);
	cmd.AddValue("dataRate", "data rate [Gb/s])", dataRate);
	cmd.AddValue("slowdataRate", "data rate [Gb/s])", slow_dataRate);
	//cmd.AddValue("interPacketInterval", "Inter packet interval [ms])", interPacketInterval);
	cmd.AddValue("goldUser", "gu", gold_user);
	cmd.AddValue("silverUser", "su", silver_user);
	cmd.AddValue("plotSinr", "plot sinr", plot_sinr);
	cmd.AddValue("interSiteDistance", "interSiteDistance", interSiteDistance);
	cmd.AddValue("interferer", "interferer", interferer);
	cmd.AddValue("n1", "n1", n1);
	cmd.AddValue("n2", "n2", n2);
	cmd.AddValue("n3", "n3", n3);
	cmd.AddValue("bs", "bs", bs);
	cmd.AddValue("weight", "weight", weight);
	cmd.AddValue("ack", "ack", ack);
	cmd.AddValue("udp", "udp", udp);
	cmd.AddValue("dynamic", "dynamic", dynamic);
	cmd.AddValue("maintain_thr", "maintain_thr", maintain_thr);
	cmd.AddValue("rate_maintain_users", "rate_maintain_users", rate_maintain_users);
	cmd.AddValue("random_location", "random_location", random_location);
	cmd.AddValue("fading", "fading", fading);
	cmd.AddValue("interval_mcs", "interval_mcs", interval_mcs);
	cmd.AddValue("interval_requirement", "interval_requirement", interval_requirement);
	
	Config::SetDefault ("ns3::LteUePhy::TxPower", DoubleValue (15));
	
	cmd.Parse(argc, argv);
	ConfigStore config;
	config.ConfigureDefaults ();
	numberOfNodes = n1 + n2 + n3;
	Config::SetDefault ("ns3::TcpL4Protocol::SocketType", TypeIdValue (TcpNewReno::GetTypeId ()));
	
	if (rate_maintain_users) dynamic = true;
	if (interferer == 1) bs = 3;

	Ptr<LteHelper> lteHelper = CreateObject<LteHelper> ();
	lteHelper->SetAttribute ("PathlossModel", StringValue ("ns3::FriisPropagationLossModel"));
	Ptr<PointToPointEpcHelper> epcHelper = CreateObject<PointToPointEpcHelper> ();
	lteHelper->SetEpcHelper (epcHelper);
	Ptr<LteEnbRrc> rrc = CreateObject<LteEnbRrc> ();
	if (ack == 1) {
		rrc->SetAttribute ("EpsBearerToRlcMapping", EnumValue (LteEnbRrc::RLC_AM_ALWAYS));
		Config::SetDefault ("ns3::LteEnbRrc::EpsBearerToRlcMapping",EnumValue(LteEnbRrc::RLC_AM_ALWAYS));
 	}
 	// below fading model

	if (fading) {
 	
	lteHelper->SetAttribute ("FadingModel", StringValue ("ns3::TraceFadingLossModel"));

	std::ifstream ifTraceFile;
	ifTraceFile.open ("../../src/lte/model/fading-traces/fading_trace_EPA_3kmph.fad", std::ifstream::in);
	if (ifTraceFile.good ())
	{
		// script launched by test.py
		lteHelper->SetFadingModelAttribute ("TraceFilename", StringValue ("../../src/lte/model/fading-traces/fading_trace_EPA_3kmph.fad"));
	}
	else
	{
		// script launched as an example
		lteHelper->SetFadingModelAttribute ("TraceFilename", StringValue ("src/lte/model/fading-traces/fading_trace_EPA_3kmph.fad"));
	}
	}

	// below two lines disable errors on CTRL and DATA:
	//Config::SetDefault ("ns3::LteSpectrumPhy::CtrlErrorModelEnabled", BooleanValue (false));
	//Config::SetDefault ("ns3::LteSpectrumPhy::DataErrorModelEnabled", BooleanValue (false));

//lteHelper->SetEnbDeviceAttribute ("DlBandwidth", UintegerValue (25));
//lteHelper->SetEnbDeviceAttribute ("UlBandwidth", UintegerValue (100));
	

	// scheduler
	//lteHelper->SetSchedulerType ("ns3::RrFfMacScheduler");

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
	for (uint16_t i = 0; i < numberOfNodes; i++) {
		PointToPointHelper* p2ph = new PointToPointHelper();
		//if (i<numberOfNodes / 2)
		if (i % 2 == 0 || i < rate_maintain_users || i >= n1)//(i<8)
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

	NodeContainer ueNodes;
	NodeContainer enbNodes;
	enbNodes.Create(bs);
	ueNodes.Create(numberOfNodes);

	// Install Mobility Model
	Ptr<ListPositionAllocator> positionAlloc = CreateObject<ListPositionAllocator> ();

	for (uint16_t i = 0; i < n1; i++) {
		if (random_location) {
			if (i < rate_maintain_users) {
				positionAlloc->Add (Vector(distance, 0, 0));
				continue;
			}
			int x, y;
			generate_x_y(distance, x, y);
			std::cout<<x<<" "<<y<<std::endl;
			positionAlloc->Add (Vector(x, y, 0));
		}
		else positionAlloc->Add (Vector(distance, 0, 0));
	}
	for (uint16_t i = 0; i < n2; i++)
		positionAlloc->Add (Vector(-distance2/2.0, distance2*1.732/2, 0));
	for (uint16_t i = 0; i < n3; i++)
		positionAlloc->Add (Vector(-distance2/2.0, -distance2*1.732/2, 0));

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
	//Config::SetDefault ("ns3::LteEnbPhy::TxPower", DoubleValue (macroEnbTxPowerDbm));
	
	lteHelper->SetEnbAntennaModelType ("ns3::ParabolicAntennaModel");
	lteHelper->SetEnbAntennaModelAttribute ("Beamwidth",   DoubleValue (70));
	lteHelper->SetEnbAntennaModelAttribute ("MaxAttenuation",     DoubleValue (20.0));
	 
	//lteHelper->SetEnbAntennaModelType ("ns3::CosineAntennaModel");
	//lteHelper->SetEnbAntennaModelAttribute ("Beamwidth",   DoubleValue (70));
	//lteHelper->SetEnbAntennaModelAttribute ("MaxGain",     DoubleValue (0.0));

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

	for (uint16_t i = 0; i < numberOfNodes; i++)
	{
		//lteHelper->Attach (ueLteDevs.Get(i), enbLteDevs.Get(0));
		lteHelper->Attach (ueLteDevs.Get(i));
		// side effect: the default EPS bearer will be activated
	}  

	std::cout<<"Print out IMSI"<<std::endl;
	for (uint16_t u = 0; u < ueNodes.GetN (); u++) {
		uint64_t imsi = ueLteDevs.Get (u)->GetObject<LteUeNetDevice> ()->GetImsi ();
		std::cout<<imsi<<std::endl;
		(*imsi_id)[imsi] = u;
	}

	// bearer      
	/*
	for (uint16_t u = 0; u < ueNodes.GetN (); u++)
	{
		Ptr<NetDevice> ueDevice = ueLteDevs.Get (u);

		GbrQosInformation qos;
		qos.gbrDl = 132;  // bit/s, considering IP, UDP, RLC, PDCP header size
		qos.gbrUl = 132;
		qos.mbrDl = qos.gbrDl;
		qos.mbrUl = qos.gbrUl;

		enum EpsBearer::Qci q;
		if (u < gold_user) (*id_weight)[u] = weight;//q = EpsBearer::NGBR_VOICE_VIDEO_GAMING;
		else if (u < gold_user + silver_user) (*id_weight)[u] = 2;//q=EpsBearer::NGBR_VIDEO_TCP_PREMIUM; 
		else (*id_weight)[u] = 1;


		q = EpsBearer::NGBR_VIDEO_TCP_DEFAULT;
		EpsBearer bearer (q);
		uint8_t bid = lteHelper->ActivateDedicatedEpsBearer (ueDevice, bearer, EpcTft::Default ());
		std::cout<<u<<"'s bearer id: "<<(int)bid<<std::endl;
	}*/

	// Install and start applications on UEs and remote host
	uint16_t dlPort = 33333;
	uint16_t ulPort = 2000;
	uint16_t otherPort = 3000;
	ApplicationContainer clientApps;
	ApplicationContainer serverApps;
	for (uint32_t u = 0; u < ueNodes.GetN (); ++u)
	{
		if (interferer == 0)
			if (u==n1) break;

		++ulPort;
		++otherPort;
		PacketSinkHelper dlPacketSinkHelper ("ns3::TcpSocketFactory", InetSocketAddress (Ipv4Address::GetAny (), dlPort));
		//PacketSinkHelper ulPacketSinkHelper ("ns3::UdpSocketFactory", InetSocketAddress (Ipv4Address::GetAny (), ulPort));
		//PacketSinkHelper packetSinkHelper ("ns3::UdpSocketFactory", InetSocketAddress (Ipv4Address::GetAny (), otherPort));
		serverApps.Add (dlPacketSinkHelper.Install (ueNodes.Get(u)));
		//serverApps.Add (ulPacketSinkHelper.Install (remoteHost));
		//serverApps.Add (packetSinkHelper.Install (ueNodes.Get(u)));

		//TcpClientHelper dlClient (ueIpIface.GetAddress (u), dlPort);

		if (! udp)
		{
			BulkSendHelper dlClient ("ns3::TcpSocketFactory",InetSocketAddress (ueIpIface.GetAddress (u), dlPort));
			dlClient.SetAttribute ("MaxBytes", UintegerValue (0));
			Ptr<Node> remoteHost = remoteHostContainer.Get (u);
			clientApps.Add(dlClient.Install(remoteHost));

		} else {
			UdpClientHelper dlClient (ueIpIface.GetAddress (u), dlPort);
			dlClient.SetAttribute ("Interval", TimeValue (MicroSeconds(1000)));
			dlClient.SetAttribute ("MaxPackets", UintegerValue(10000000));
			Ptr<Node> remoteHost = remoteHostContainer.Get (u);
			clientApps.Add(dlClient.Install(remoteHost));
		}

		// sender infor, check later.
		/*
		UdpClientHelper ulClient (remoteHostAddr, ulPort);
		ulClient.SetAttribute ("Interval", TimeValue (MilliSeconds(interPacketInterval)));
		ulClient.SetAttribute ("MaxPackets", UintegerValue(1000000));

		UdpClientHelper client (ueIpIface.GetAddress (u), otherPort);
		client.SetAttribute ("Interval", TimeValue (MilliSeconds(interPacketInterval)));
		client.SetAttribute ("MaxPackets", UintegerValue(1000000));
		*/
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
	//serverApps.Start (Seconds (1.0));
	//clientApps.Start (Seconds (1.0));
	clientApps.Get(0)->SetStartTime(Seconds(1));
	serverApps.Get(0)->SetStartTime(Seconds(1));
	ApplicationContainer::Iterator i;
	int n = 1;
	int first_started = 20;
	for (i = clientApps.Begin ()+1; i != clientApps.End (); ++i) {
		if (n>first_started && n<n1)
		{
			(*i)->SetStartTime(Seconds((n-first_started)*5.0));
			(*i)->SetStopTime(Seconds((n-first_started)*5.0 + (n1-n)*10.0));
		}
		else
			(*i)->SetStartTime(Seconds(1));
		n += 1;
	}
	n = 1;
	for (i = serverApps.Begin ()+1; i != serverApps.End (); ++i) {
		if (n>first_started && n<n1)
		{
			(*i)->SetStartTime(Seconds((n-first_started)*5.0));
			(*i)->SetStopTime(Seconds((n-first_started)*5.0 + (n1-n)*10.0));
		}
		else
			(*i)->SetStartTime(Seconds(1));
		n += 1;
	}
	lteHelper->EnableTraces ();


	if (dynamic)
	{
		for (float i=0; i<simTime; i+=interval_mcs)
			Simulator::Schedule(Seconds(i), &dynamic_maintain);

		for (float i=0; i<simTime; i+=interval_requirement)
			Simulator::Schedule(Seconds(i), &clear_prb);
	}
	
	Ptr <FlowMonitor> flowmon;
	FlowMonitorHelper fmHelper;
	flowmon = fmHelper.Install (ueNodes);
	flowmon = fmHelper.Install (remoteHostContainer);
	Simulator::Schedule(Seconds(3), &ThroughputMonitor, &fmHelper, flowmon); 


	//Simulator::Schedule(Seconds(8), &modify_requirement, numberOfNodes, ndc);
        Config::Connect ("/NodeList/*/DeviceList/*/LteEnbRrc/ConnectionEstablished", MakeCallback (&NotifyConnectionEstablishedEnb));
	Simulator::Stop(Seconds(simTime));

	Ptr<RadioEnvironmentMapHelper> remHelper;
	int bound = 20000;
	if (plot_sinr) {
		PrintGnuplottableToFile ();
		remHelper = CreateObject<RadioEnvironmentMapHelper> ();
		std::ostringstream temp;
		temp << numberOfNodes;
		remHelper->SetAttribute ("ChannelPath", StringValue ("/ChannelList/" + temp.str()));
		remHelper->SetAttribute ("OutputFile", StringValue ("rem.out"));
		remHelper->SetAttribute ("XMin", DoubleValue (-bound));
		remHelper->SetAttribute ("XMax", DoubleValue (bound));
		remHelper->SetAttribute ("XRes", UintegerValue (100));
		remHelper->SetAttribute ("YMin", DoubleValue (-bound));
		remHelper->SetAttribute ("YMax", DoubleValue (bound));
		remHelper->SetAttribute ("YRes", UintegerValue (100));
		remHelper->SetAttribute ("Z", DoubleValue (0.0));
		remHelper->SetAttribute ("UseDataChannel", BooleanValue (false));
		remHelper->SetAttribute ("RbId", IntegerValue (-1));
		remHelper->Install ();
	}

	config.ConfigureAttributes ();

	char buff[100];
	std::cout<<"PCAP"<<std::endl;
	for (uint8_t i=0; i<ueNodes.GetN (); ++i) {
		if (interferer == 0)
			if (i==n1) break;

		//sprintf(buff, "trace_nonsharing_d%d_gu%d_su%d_r%sGb_id%d.pcap", (int)distance, gold_user, silver_user, dataRate.c_str(), i);
		sprintf(buff, "dynamic_weight_%d.pcap", i);
		std::string buffAsStdStr = buff;
		std::cout<<remoteHostContainer.Get(i)->GetNDevices()<<std::endl;
		p2pv[i]->EnablePcap(buffAsStdStr, remoteHostContainer.Get(i)->GetDevice(1), false, true);
	}

	Simulator::Run();

	Simulator::Destroy();
	return 0;
}
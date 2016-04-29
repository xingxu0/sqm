#include <map>

std::map <uint64_t, uint16_t> * imsi_id;
std::map <uint16_t, uint64_t> * rnti_imsi;
std::map <uint16_t, float> * id_weight;

std::map <uint16_t, uint32_t> * rnti_mcs;
std::map <uint16_t, uint16_t> * rnti_mcs_count;
std::map <uint16_t, double> * rnti_rate;

std::map <uint16_t, uint16_t> * rnti_prbs;

void init() {
	imsi_id = new std::map <uint64_t, uint16_t>();
	rnti_imsi = new std::map <uint16_t, uint64_t>();
	id_weight = new std::map<uint16_t, float>();
	rnti_mcs = new std::map <uint16_t, uint32_t>();
	rnti_mcs_count = new std::map <uint16_t, uint16_t>();
	rnti_rate = new std::map<uint16_t, double>();
	rnti_prbs = new std::map<uint16_t, uint16_t>();
}
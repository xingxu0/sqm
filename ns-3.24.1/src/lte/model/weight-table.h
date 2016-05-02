#include <map>
typedef uint8_t mcs_log[29];

std::map <uint64_t, uint16_t> * imsi_id;
std::map <uint16_t, uint64_t> * rnti_imsi;
std::map <uint16_t, float> * id_weight;

std::map <uint16_t, uint32_t> * rnti_mcs;
std::map <uint16_t, uint16_t> * rnti_mcs_count;
std::map <uint16_t, double> * rnti_rate;

std::map <uint16_t, uint16_t> * rnti_prbs;

std::map <uint16_t, uint32_t> * rnti_mcs_selected;
std::map <uint16_t, uint16_t> * rnti_mcs_count_selected;

std::map <uint16_t, uint16_t> * rnti_mcs_max;

std::map <uint16_t, mcs_log> * rnti_mcs_log;

void init() {
	imsi_id = new std::map <uint64_t, uint16_t>();
	rnti_imsi = new std::map <uint16_t, uint64_t>();
	id_weight = new std::map<uint16_t, float>();
	rnti_mcs = new std::map <uint16_t, uint32_t>();
	rnti_mcs_count = new std::map <uint16_t, uint16_t>();
	rnti_rate = new std::map<uint16_t, double>();
	rnti_prbs = new std::map<uint16_t, uint16_t>();
	
	// mcs value when this user got selected
	rnti_mcs_selected = new std::map <uint16_t, uint32_t>();
	rnti_mcs_count_selected = new std::map <uint16_t, uint16_t>();
	
	rnti_mcs_max = new std::map <uint16_t, uint16_t>();
	rnti_mcs_log = new std::map<uint16_t, mcs_log>();
}

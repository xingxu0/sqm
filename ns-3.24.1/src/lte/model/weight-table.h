#include <map>

std::map <uint64_t, uint16_t> * imsi_id;
std::map <uint16_t, uint64_t> * rnti_imsi;
std::map <uint16_t, float> * id_weight;

std::map <uint16_t, uint8_t> * rnti_mcs;
std::map <uint16_t, double> * rnti_rate;

std::map <uint16_t, uint16_t> * rnti_prbs;


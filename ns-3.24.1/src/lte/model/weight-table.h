#ifndef WEIGHT_TABLE_H
#define WEIGHT_TABLE_H

#include <ns3/lte-common.h>
#include <map>
struct mcs_log { uint16_t mcs[29]; };

extern std::map <uint64_t, uint16_t> * imsi_id;
extern std::map <uint16_t, uint64_t> * rnti_imsi;
extern std::map <uint16_t, float> * id_weight;

extern std::map <uint16_t, uint32_t> * rnti_mcs;
extern std::map <uint16_t, uint16_t> * rnti_mcs_count;
extern std::map <uint16_t, double> * rnti_rate;

extern std::map <uint16_t, uint16_t> * rnti_prbs;
extern std::map <uint16_t, uint16_t> * rnti_prbs_previous;

extern std::map <uint16_t, uint32_t> * rnti_mcs_selected;
extern std::map <uint16_t, uint16_t> * rnti_mcs_count_selected;

extern std::map <uint16_t, uint16_t> * rnti_mcs_max;

extern std::map <uint16_t, mcs_log> * rnti_mcs_log;

extern std::map <uint16_t, uint64_t> * rnti_am_mode_bytes_adjustment; // to adjust AM bytes according to uplink traffic's STATUS PDU

void init();

#endif
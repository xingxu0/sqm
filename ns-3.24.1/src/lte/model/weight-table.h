#include <map>

std::map <uint64_t, uint16_t> * imsi_id;
std::map <uint16_t, uint64_t> * rnti_imsi;
std::map <uint16_t, float> * id_weight;

std::map <uint16_t, uint8_t> * rnti_mcs;
std::map <uint16_t, double> * rnti_rate;

std::map <uint16_t, uint16_t> * rnti_prbs;

static const int McsToItbs[29] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 10, 11, 12, 13, 14, 15, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26};

int GetTbSizeFromMcs (int mcs, int nprb)
{
	int itbs = McsToItbs[mcs];
	return (TransportBlockSizeTable[nprb - 1][itbs]);
}


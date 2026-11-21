// hautbackenkerne — alle CUDA-Kerne des lokalen Backers (21.11.2026, Edgar: „Warp überall raus“; bis dahin rund 65 Warp-Kerne in `core/dienste/hautbacken`).
// Übersetzt mit -fmad=true wie Warps Vorgabe; die Rechnungen stehen in Warps Form (`wp17.cuh`). Der Strahl auf den Körper kommt aus
// `Assets/kartenkoepfe/kartenstrahl.cuh` (Warp 1.17 `mesh_query_ray`) über GarmentCodes `Dreiecksbaum`.
#include "kartenstrahl.cuh"
#include "hautbackenkern.cuh"
#include "hautkontextkern.cuh"
#include "hauttexturkern.cuh"
#include "hautclosurekern.cuh"
#include "hautknotenaus.cuh"

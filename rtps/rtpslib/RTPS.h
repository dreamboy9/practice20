#ifndef RTPS_RTPS_H_INCLUDED
#define RTPS_RTPS_H_INCLUDED

#include <vector>

//OpenCL API
#include "opencl/CLL.h"

//Render API
#include "render/Render.h"

//System API
#include "system/System.h"

//initial value API
#include "particle/IV.h"

//settings class to configure the framework
#include "RTPSettings.h"

// Timer class
#include <timege.h>

//defines useful structs like float3 and float4
#include "util.h"

namespace rtps {

class RTPS
{
public:
	// Timers
	enum {TI_SYSTEM_UPDATE=0, TI_RENDER_UPDATE};
	GE::Time* ts_cl[20];   // ts_cl  is GE::Time**

public:
    //default constructor
    RTPS();
    //Setup CL, Render, initial values and System based on settings
    RTPS(RTPSettings s);

    ~RTPS();

	//--------------------
	// Gordon additions
	//void setTimers(GE::Time** timers) {
		//this->ts_cl = timers;
	//}
	//--------------------

    void Init();

    //Keep track of settings
    RTPSettings settings;
    
    //OpenCL abstraction instance
    CL *cli;
    Render *renderer;

    //will be instanciated as a specific subclass like SPH or Boids
    System *system;
    //std::vector<System> systems;

    //initial value helper
    //IV iv;


    void update();
    void render();
};

}

#endif

#include "RTPSettings.h"
namespace rtps
{


    RTPSettings::RTPSettings()
    {
        system = SPH;
        max_particles = 2048;
        dt = .001f;
        grid = Domain(float4(-5,-.3f,0,0), float4(2, 2, 12, 0));
    }

    RTPSettings::RTPSettings(SysType system, int max_particles, float dt)
    {
        this->system = system;
        this->max_particles = max_particles;
        this->dt = dt;
        grid = Domain(float4(-5,-.3f,0,0), float4(2, 2, 12, 0));
    }

    RTPSettings::RTPSettings(SysType system, int max_particles, float dt, Domain grid)
    {
        this->system = system;
        this->max_particles = max_particles;
        this->dt = dt;
        this->grid = grid;
    }

    //with triangle collision
    RTPSettings::RTPSettings(SysType system, int max_particles, float dt, Domain grid, bool tri_collision)
    {
        this->system = system;
        this->max_particles = max_particles;
        this->dt = dt;
        this->grid = grid;
        this->tri_collision = tri_collision;
    }
    
    RTPSettings(SysType system, int max_particles, float dt, Domain grid, float maxspeed, float mindist, float searchradius, float color[], float w_sep, float w_align, float w_coh);
    {
        this->system = system;
        this->max_particles = max_particles;
        this->dt = dt;
        this->grid = grid;
        this->max_speed = maxspeed;
        this->min_dist = mindist;
        this->search_radius = searchradius;
        this->color = float4(color[0], color[1], color[2],1.f);
        this->w_sep = w_sep;
        this->w_align = w_align;
        this->w_coh = w_coh;
    }
}

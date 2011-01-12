#ifndef RTPS_KINECT_H_INCLUDED
#define RTPS_KINECT_H_INCLUDED

#include <string>

#include "../RTPS.h"
#include "System.h"
#include "ForceField.h"
#include "../opencl/Kernel.h"
#include "../opencl/Buffer.h"
//#include "../util.h"

#include <ntk/camera/kinect_grabber.h>
#include <ntk/camera/rgbd_processor.h>
#include <ntk/camera/calibration.h>
#include <ntk/utils/opencv_utils.h>
//#include <ntk/utils/arg.h>
#include <ntk/geometry/pose_3d.h>


namespace rtps {


class Kinect : public System
{
public:
    Kinect(RTPS *ps, int num);
    ~Kinect();

    void update();

    bool forcefields_enabled;
    int max_forcefields;

    //the particle system framework
    RTPS *ps;

    std::vector<float4> positions;
    std::vector<float4> colors;
    std::vector<float4> velocities;
    std::vector<float4> forces;
    std::vector<ForceField> forcefields;


    Kernel k_forcefield;
    Kernel k_euler;

    Buffer<float4> cl_position;
    Buffer<float4> cl_color;
    Buffer<float4> cl_force;
    Buffer<float4> cl_velocity;
    Buffer<ForceField> cl_forcefield;
    Buffer<float4> cl_kinect;
    

    void loadForceField();
    void loadForceFields(std::vector<ForceField> ff);
    void loadEuler();

    void cpuForceField();
    void cpuEuler();

    //kinect
    
    ntk::RGBDCalibration calibration;
    ntk::KinectGrabber grabber;
    ntk::RGBDProcessor processor;
    ntk::RGBDImage current_frame;
    cv::Mat3b mapped_color;
 
    
};

}

#endif
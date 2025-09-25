# Application of the LISFLOOD-FP Hydrodynamic Model for Impact-Based Forecasting over the Eastern Africa Region


### LISFLOOD-FP 8.1

Source from https://zenodo.org/records/6912932


### To get the source code of RIM2D model

RIM2D is a 2D hydraulic inundation model specifically designed for fluvial and
pluvial flood simulation. RIM2D has simplified approaches implemented for
simulating sewer system, roof drainage and infiltration. Thus it is well suited
for fast urban inundation simulation. RIM2D is coded in Fortran90 and runs the
simulations on GPUs. Compiling thus requires a NVIDIA CUDA enabled Fortran
compiler.

Developed by Section 4.4 Hydrology of the GFZ German Research Centre for
Geoscience

Repository created by Dr. Heiko Apel, heiko.apel@gfz-potsdam.de

Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Section
4.4 Hydrology, 14473 Potsdam, Germany

# RIM2D Quick Start Guide

## Overview
RIM2D is a super fast 2D hydraulic inundation model designed for fluvial and pluvial flood simulation that runs on NVIDIA GPUs using CUDA Fortran.

## GPU Status Check
✅ **NVIDIA GPU Detected**: GeForce RTX 5050 (8GB VRAM)
- Driver Version: 580.82.07
- CUDA Version: 13.0
- GPU is available and ready for RIM2D

## Prerequisites

### Required Software
- **NVIDIA HPC Toolkit** with `nvfortran` compiler (REQUIRED)
- **NetCDF Fortran libraries** compiled with nvfortran
- **CMake** for building
- **Git** (already available)

### Current Status
- ❌ `nvfortran` - Not installed (required for compilation)
- ❌ `gfortran` - Not installed (alternative not suitable for GPU code)
- ✅ Sample datasets available in `example_fluvial/` and `example_pluvial/`

## Installation Steps

### 1. Install NVIDIA HPC SDK 2025 (Version 25.7)
```bash
# Download NVIDIA HPC SDK 2025 (8.3GB - ensure sufficient space)
wget https://developer.download.nvidia.com/hpc-sdk/25.7/nvhpc_2025_257_Linux_x86_64_cuda_12.9.tar.gz

# Extract the archive
tar xpzf nvhpc_2025_257_Linux_x86_64_cuda_12.9.tar.gz

# Install (requires sudo for system-wide installation)
sudo ./nvhpc_2025_257_Linux_x86_64_cuda_12.9/install

# Add to PATH (add to ~/.bashrc for permanent)
export PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/25.7/compilers/bin:$PATH
export LD_LIBRARY_PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/25.7/compilers/lib:$LD_LIBRARY_PATH

# Verify installation
nvfortran --version
```

**Alternative: Package Manager Installation (RHEL/CentOS/Fedora)**
```bash
sudo dnf config-manager --add-repo https://developer.download.nvidia.com/hpc-sdk/rhel/nvhpc.repo
sudo dnf install -y nvhpc-25.7
```

### 2. Set Environment Variables
```bash
# Set environment variables for netcdf-fortran compiled with nvfortran
export NETCDF_LIB="-L/home/roller/Desktop/rim2d/lib -lnetcdff -lnetcdf"
export NETCDF_INCLUDE="-I/home/roller/Desktop/rim2d/include"
export LD_LIBRARY_PATH="/home/roller/Desktop/rim2d/lib:$LD_LIBRARY_PATH"

# Set preferred compilers
export FC=nvfortran
export F77=nvfortran
export CC=nvc
export CXX=nvc++

# Optional: Add to ~/.bashrc for permanent setup
echo 'export PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/25.7/compilers/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/25.7/compilers/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
echo 'export FC=nvfortran' >> ~/.bashrc
echo 'export F77=nvfortran' >> ~/.bashrc
echo 'export CC=nvc' >> ~/.bashrc
echo 'export CXX=nvc++' >> ~/.bashrc
```

### 3. Install System Dependencies (Critical)
```bash
# Install required build tools (CRITICAL - Claude compilation failed without these)
sudo apt update
sudo apt install -y m4 autoconf libtool build-essential

# Verify critical dependencies are available
which m4 || { echo "FATAL: m4 required but not found"; exit 1; }
which autoconf || { echo "FATAL: autoconf required"; exit 1; }
which libtool || { echo "FATAL: libtool required"; exit 1; }
```

### 4. Install NetCDF Dependencies
```bash
# Install NetCDF libraries compiled with nvfortran
# This script compiles: zlib-ng → HDF5 → NetCDF-C → NetCDF-Fortran
bash install-deps

# Verify NetCDF installation
ls -la lib/libnetcdf*.so
ls -la include/netcdf*.mod
```

### 5. Compile RIM2D
```bash
# Compile and install RIM2D executable
bash install-RIM2D

# Verify RIM2D compilation
ls -la bin/RIM2D
file bin/RIM2D  # Should show: ELF 64-bit executable
```

## Sample Datasets

### Fluvial Example (Ahr River Flood 2021)
- **Location**: `example_fluvial/`
- **Definition file**: `Altenahr-Sinzig_flood2021_reconstructed_10m.def`
- **Description**: Complete fluvial flood simulation for the Ahr river, Germany
- **Input files**: DEM, buildings, roughness, inflow data, etc.

### Pluvial Example (Klotzsche, Dresden)
- **Location**: `example_pluvial/`
- **Definition file**: `Klotzsche_example_2018_06_01.def`
- **Description**: Urban pluvial flood simulation test case
- **Input files**: DEM, buildings, precipitation, sewer system data

## Running RIM2D

### IMPORTANT: Correct Directory Structure
RIM2D expects relative paths defined in `.def` files. You must run from the correct directory:

```bash
# ❌ WRONG - Run from main directory causes "No such file or directory" errors
./bin/RIM2D example_fluvial/Altenahr-Sinzig_flood2021_reconstructed_10m.def
# Error: FIO-F-/OPEN/unit=2/error code returned by host stdio - 2.
# File name = ./input/Altenahr-Sinzig_inflow_flood2021_reconstructed_10m.txt

# ✅ CORRECT - Run from example directory
cd example_fluvial
../bin/RIM2D Altenahr-Sinzig_flood2021_reconstructed_10m.def
```

### Pre-Run Setup
```bash
# Create output directories (required)
cd example_fluvial
mkdir -p output

cd ../example_pluvial
mkdir -p output
```

### Basic Usage
```bash
# Fluvial example (run from example_fluvial/)
cd example_fluvial
../bin/RIM2D Altenahr-Sinzig_flood2021_reconstructed_10m.def

# Pluvial example (run from example_pluvial/)
cd example_pluvial
../bin/RIM2D Klotzsche_example_2018_06_01.def
```

### Monitor Simulation Progress
```bash
# RIM2D simulations can take time - monitor output files
watch -n 5 'ls -la output/'

# Check simulation status in another terminal
ps aux | grep RIM2D

# Monitor GPU usage during simulation
watch -n 2 nvidia-smi
```

### Quick Test Commands
```bash
# Test fluvial example (15 hour flood simulation)
cd example_fluvial && mkdir -p output && ../bin/RIM2D Altenahr-Sinzig_flood2021_reconstructed_10m.def

# Test pluvial example (urban flood simulation)
cd example_pluvial && mkdir -p output && ../bin/RIM2D Klotzsche_example_2018_06_01.def
```

## File Formats
- `.f` - Fortran90 source code
- `.cuf` - CUDA Fortran source code (GPU code)
- `.def` - RIM2D model definition files
- `.asc` - ESRI ASCII raster files
- `.nc` - NetCDF raster files

## Troubleshooting

### Common Issues

#### Compilation Problems
1. **nvfortran not found**: Install NVIDIA HPC Toolkit and set PATH
2. **NetCDF errors**: Run `bash install-deps` to install compatible libraries
3. **"Cannot find m4 utility"**: Install system dependencies first:
   ```bash
   sudo apt install -y m4 autoconf libtool build-essential
   ```
4. **CMake errors**: Delete `CMakeCache.txt` and retry compilation
5. **GPU not detected**: Ensure NVIDIA drivers are installed and `nvidia-smi` works

#### Runtime Problems
6. **"No such file or directory" (input files)**:
   - Run RIM2D from the example directory, not the main directory
   - Correct: `cd example_fluvial && ../bin/RIM2D file.def`
   - Wrong: `./bin/RIM2D example_fluvial/file.def`
7. **"No such file or directory" (output files)**: Create output directory:
   ```bash
   mkdir -p output
   ```
8. **Simulation hangs/slow**: Normal behavior for large simulations, monitor with `nvidia-smi`

### Verification Commands
```bash
# Check GPU status
nvidia-smi

# Check compiler availability
nvfortran --version

# Check compilation status
ls -la bin/RIM2D

# Test NetCDF libraries
ls -la lib/libnetcdf*.so
ls -la include/netcdf*.mod

# Verify input files exist
ls -la example_fluvial/input/
ls -la example_pluvial/input/

# Check if simulation is running
ps aux | grep RIM2D
```

## System Requirements Summary
- **GPU**: NVIDIA GPU with CUDA support (✅ RTX 5050 detected)
- **Disk Space**: ~20GB for HPC SDK installation + workspace
- **Memory**: Adequate RAM for compilation and simulation
- **OS**: Linux x86_64 (✅ Detected: Linux 6.12.43+deb12-amd64)

## Current System Status
✅ **GPU Available**: NVIDIA GeForce RTX 5050 (8GB VRAM)
✅ **Sample Data**: Located in example_fluvial/ and example_pluvial/
✅ **Build Environment**: Basic tools available
❌ **nvfortran**: Not installed (required for compilation)
❌ **NetCDF**: Will be installed after nvfortran

## Next Steps (In Order)
1. **Install NVIDIA HPC SDK 2025** - Download 8.3GB package and run installer
2. **Set environment variables** - Configure PATH and compiler settings
3. **Install dependencies** - Run `bash install-deps` to build NetCDF libraries
4. **Compile RIM2D** - Run `bash install-RIM2D` to build executable
5. **Test with sample data** - Run fluvial or pluvial examples

## Estimated Time
- Download: 30-60 minutes (depending on connection)
- Installation: 10-15 minutes
- Compilation: 5-10 minutes
- **Total**: ~1-2 hours for complete setup

## Compilation Analysis Results

### Manual vs Automated Compilation
Based on detailed analysis comparing manual and Claude-assisted compilation:

**✅ Manual Compilation Success Factors:**
- Complete build environment with all system tools (m4, autoconf, libtool)
- Proper dependency chain: zlib-ng → HDF5 → NetCDF-C → NetCDF-Fortran
- Correct environment variables and compiler paths

**❌ Common Automated Compilation Failures:**
- Missing system dependencies (especially m4 utility)
- Incomplete environment checking before compilation
- Path and working directory issues

**🔧 Key Lessons Learned:**
1. **System dependencies are critical** - Install m4, autoconf, libtool first
2. **Environment verification required** - Check all tools before starting
3. **Staged compilation works best** - Verify each component before proceeding
4. **Working directory matters** - Run from correct paths for relative file references

See `RIM2D_COMPILATION_ANALYSIS.md` for detailed failure analysis.

## Resources
- **This Guide**: `RIM2D_QUICK_START_GUIDE.md` (current file)
- **Compilation Analysis**: `RIM2D_COMPILATION_ANALYSIS.md` (detailed troubleshooting)
- **Previous Failures**: `rim2d-netcdf.md` (Claude compilation issues)
- **Documentation**: `RIM2D documentation.pdf`
- **Workflow Guide**: `Workflow RIM2D model setup.pdf`
- **Compilation Details**: `readme_compiling.md`
- **NVIDIA HPC SDK**: https://developer.nvidia.com/hpc-sdk


```
output  readme.md
(zarrv3) roller@debian:~/Desktop/rim2d/example_fluvial$ ../bin/RIM2D Altenahr-Sinzig_flood2021
 ******************************************************
 INFO: read simulation definition from:
 Altenahr-Sinzig_flood2021_reconstructed_10m.def
 Use GPU device:            0
 DEM used (gokf):
 ./input/Altenahr-Sinzig_DEM10_housesnodata_box.asc
 Sewershed mask raster (maskf):
 ./input/Altenahr-Sinzig_sewershed_box.asc
 inflow hydroraph file (infloc):
 ./input/Altenahr-Sinzig_inflow_flood2021_reconstructed_10m.txt
 Impervious surface grid: ./input/Altenahr-Sinzig_sealed_surface_box.asc
 Pervious surface grid: ./input/Altenahr-Sinzig_pervious_surface_box.asc
 roof/house grid: ./input/Altenahr-Sinzig_buildings_box.asc
 Roughness coefficient=file:
 ./input/Altenahr-Sinzig_roughness_DEM10_new_forest02.asc
 initial water depth=file: ./input/Altenahr-Sinzig_iwd_163.2.asc
 number of precipitation files =             0
 time step between precipitation files =           300
 start of precipitation at sec =             0
 precipitation files base name = ./input/rain/20210714-0750_t
 goutf:
 ./output/Altenahr-Sinzig_fluvial_flood2021_reconstructed_10m_
 number of intermediate output grids:           12
 grid output times:         3600         7200        10800        14400
        21600        25200        28800        32400        36000        39600
        43200        46800
 time step [seconds] -> dt=    1.000000000000000
 Simulation time [seconds] -> duration=    54000.00000000000
 infiltration rate:     0.000000000000000
 sewer capacity:     0.000000000000000
 sewthresh =    2.0000000000000000E-003
 alpha =    0.5000000000000000
 theta =    0.8000000000000000
 verbose:  F
 routing:  T
 superverbose:  F
 neg_wd_corr:  T
 sewer sub catchments:  F
 fluvial boundary mask:  F
 write full set of output files:  F
 boundlength =        108000
 tstep_in =           900
 number of inflow cells/regions:             6
 length of boundary time series:        108000  seconds
 time step of boundary data =           900  seconds
 number of boundary inflow cells/regions:             6
 number of outflow cells (noutloc):             7
 outflow time step (outtstep) in seconds:           300
 finished reading model definition file
 **************************************************
 verbose is OFF. model runs in quiet mode.
 ********
 DEM FILE TYPE IS ASCII
 RIM2D model output will be written as ascii
 ********
 number of sewer sub-catchments:            0
 number of fluvial boundaries:            0
 use GPU device number:             0

 Start GPU kernel

 allocate stormwater_sewsub
 boundlength=       108000
 tstep_in=          900
 ninflow=            6
 noutput=           12
 Total time including data xfer:     812.0213019847870
 ++++ Simulation finished! ++++
```

### Pluvial simulation log

```
$ ../bin/RIM2D Klotzsche_example_2018_06_01.def
 ******************************************************
 INFO: read simulation definition from:
 Klotzsche_example_2018_06_01.def
 Use GPU device:            0
 DEM used (gokf):
 ./input/Klotzsche_DEM5_housesnodata.asc
 Sewershed mask raster (maskf):
 ./input/Klotzsche_sewershed.asc
 inflow hydroraph file (infloc):./input/fluvial_boundary_none.txt
 Impervious surface grid: ./input/Klotzsche_sealed_surface.asc
 Pervious surface grid: ./input/Klotzsche_pervious_surface.asc
 roof/house grid: ./input/Klotzsche_OSM_buildings.asc
 Roughness coefficient=file: ./input/Klotzsche_roughness.asc
 initial water depth=    0.000000000000000
 number of precipitation files =            73
 time step between precipitation files =           300
 start of precipitation at sec =             0
 precipitation files base name = ./input/rain/2018_06_01_t
 end of precipitation input at sec =         21600
 goutf:
 ./output/Klotzsche_2018_06_01_sew20_
 number of intermediate output grids:           15
 grid output times:          900         1800         2700         3600
         4500         5400         6300         7200         8100         9000
         9900        10800        11700        12600        13500
 time step [seconds] -> dt=    1.000000000000000
 Simulation time [seconds] -> duration=    21900.00000000000
 infiltration rate:     20.00000000000000
 sewer capacity:     25.00000000000000
 sewthresh =    2.0000000000000000E-003
 alpha =    0.5000000000000000
 theta =    0.9500000000000000
 verbose:  F
 routing:  T
 superverbose:  F
 neg_wd_corr:  T
 sewer sub catchments:  F
 fluvial boundary mask:  F
 write full set of output files:  F
 boundlength =             0
 tstep_in =             0
 number of inflow cells/regions:             0
 length of boundary time series:             0  seconds
 time step of boundary data =             0  seconds
 number of boundary inflow cells/regions:             0
 number of outflow cells (noutloc):             0
 outflow time step (outtstep) in seconds:             0
 finished reading model definition file
 **************************************************
 verbose is OFF. model runs in quiet mode.
 ********
 DEM FILE TYPE IS ASCII
 RIM2D model output will be written as ascii
 ********
 number of sewer sub-catchments:            0
 number of fluvial boundaries:            0
 use GPU device number:             0

 Start GPU kernel

 allocate stormwater_sewsub
 boundlength=            0
 tstep_in=            0
 ninflow=            0
 noutput=           15
 Total time including data xfer:     64.31176400184631
 ++++ Simulation finished! ++++
```


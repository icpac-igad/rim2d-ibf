# RIM2D: A super fast 2D hydraulic inundation model

RIM2D is a 2D hydraulic inundation model specifically designed for fluvial and pluvial flood simulation. RIM2D has simplified approaches implemented for simulating sewer system, roof drainage and infiltration. Thus it is well suited for fast urban inundation simulation. RIM2D is coded in Fortran90 and runs the simulations on GPUs. Compiling thus requires a NVIDIA CUDA enabled Fortran compiler.

Developed by Section 4.4 Hydrology of the GFZ German Research Centre for Geoscience

Repository created by Dr. Heiko Apel, heiko.apel@gfz-potsdam.de

Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Section 4.4 Hydrology, 14473 Potsdam, Germany

# Repository structure

The repository contains the following folders:

* source - hosts the Fortran source code files
* CMake - contains the CMakeLists.txt file and instructions to compile the code with CMake, and how to run the model  
* example_fluvial - a complete example for fluvial flood simulation in the Ahr river, Germany
* example_pluvial - a complete example data set for running a pluvial flood simulation for the test case Klotzsche, Dresden

The pdf "RIM2D documentation.pdf" describes the core concept of RIM2D and file formats/contents.  
The pdf "WorkFlow RIM2D model.pdf" contains a basic guidance to setup a RIM2D model.
Both documents are very basic, but will be constantly updated.  

# File formats

* .f - Fortran90 source code
* .cuf - CUDA Fortran source code (contains GPU code)
* .def - RIM2D model definition files (ASCII text file)
* .R - R scripts
* .asc - ESRI ASCII raster files
* .nc - NetCDF raster files

# Installation

## Requirements

* a CUDA enabled NVIDIA GPU device connected to your machine/server
* the NVIDIA CUDA Fortran compiler (nvfortran) installed on the system. Currently this is available for Linux only. The Windows compiler is still under construction by NVIDIA. However, there are potential ways to compile and run the code under Windows, e.g. the Windows Subsystem for Linux (WSL 2). Not tested yet, though.
* From Version 0.1 RIM2D also needs the netcdf fortran libraries compiled with nvfortran on the system. The repo contains the bash script 'install-deps' for installing these locally with your RIM2D compilation.

## Compile from source

see [./readme_compiling.md](./readme_compiling.md)

## Model definition file formats  

Since verion v0.1 RIM2D can digest two different formats of model definition files (*.def files):   
the old fixed format, in which the entries of each line is pre-described,   
and a newer flexible format, in which the entries are marked by keywords in the preceeding line.   
Templates for the fixed format come with the example models (folders example_fluvial and example_pluvial). A template for the flexible format is provided in the root folder of the repo [./RIM2D_flexible_model_definition_file_template.def](RIM2D_flexible_model_definition_file_template.def).  
The format of the definition file can be specified by the --def flag in the call of RIM2D on the command line after the path+name to the *.def file. example:  

./RIM2D test.def --def fix  

or  

./RIM2D test.def --def flex  

If --def is not given, fixed format is assumed.

## Citing RIM2D

For referencing RIM2D, please use the following reference:

Apel, H., Vorogushyn, S., Merz, B., 2022. Brief communication - Impact Forecasting Could Substantially Improve the Emergency Management of Deadly Floods: Case Study July 2021 floods in Germany. Nat. Hazards Earth Syst. Sci. Discuss., 2022: 1-10. DOI:10.5194/nhess-2022-33

link to open access paper: https://nhess.copernicus.org/preprints/nhess-2022-33/

In addition, this repository can be cited.


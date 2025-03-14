# EtchSTL

A program for converting images into 3D plates with an etched appearance. Plates produced by this program are encoded using the STL format and can therefore be incorporated into CAD models using CSG, or 3D printed directly as art objects.

![output example](example1.png)

# Usage

```
etchstl.py [options] IMAGE

 -o FILENAME        output filename (default is stl.out)
 -t THICKNESS       plate thickness
 -p SIZE            pixel size
 -P PITCH           distance between pixels
 -d DEPTH           pixel depth
 -s SCALE           image scale (percent)
 -f SIZE            size of frame around image, in pixels
 -h                 show help
```
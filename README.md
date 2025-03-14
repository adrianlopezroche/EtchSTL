# EtchSTL

A program for converting images into 3D plates with an etched appearance. Plates produced by this program are encoded using the STL format and can therefore be incorporated into CAD models using CSG, or 3D printed directly as artistic objects.

The inspiration for this technique comes from a desire to incorporate vertical text into 3D printed designs. The most common approach for this is to make use of of embossed or debossed text, but these kinds of features tend to look better printed horizontally than when printed vertically. The method of applying text or graphics used by EtchSTL, on the other hand, is designed for vertical printing.

Meshes produced by EtchSTL are composed of alternating support and image layers. The image layers contain the "pixels" that make up the etched image while the support layers provide a flat surface upon which pixels higher up the Z axis can be printed directly. Experiments show this enables some complex shapes to be printed more cleanly than with regular embossing or debossing, albeit at the cost of resolution.

Best results can be obtained by choosing a pixel size and pitch (the distance between pixels) that is a multiple of the layer height, and preferably larger (e.g. double the layer height). The plates are best printed vertically, as the number of small features in the resulting meshes can require complex paths when printed horizontally that can overwhelm 3D slicers.

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
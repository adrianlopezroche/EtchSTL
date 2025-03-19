#!/usr/bin/python3

#
#  EtchSTL - A program for converting images into 3D plates with an etched appearance.
#
#  Copyright (c) 2025 Adrian Lopez
#
#  This software is provided 'as-is', without any express or implied
#  warranty. In no event will the authors be held liable for any damages
#  arising from the use of this software.
#
#  Permission is granted to anyone to use this software for any purpose,
#  including commercial applications, and to alter it and redistribute it
#  freely, subject to the following restrictions:
#
#  1. The origin of this software must not be misrepresented; you must not
#     claim that you wrote the original software. If you use this software
#     in a product, an acknowledgment in the product documentation would be
#     appreciated but is not required.
#  2. Altered source versions must be plainly marked as such, and must not be
#     misrepresented as being the original software.
#  3. This notice may not be removed or altered from any source distribution.
#

import struct
import getopt
import sys
import pathlib
from PIL import Image
from PIL import ImageOps

depth = 1.0
thickness = 5.0
pixel_size = 0.4
pixel_separation = 0.4
scale = 1.0
frame = 0

def addblock(blocks, x, y, width, height):
    blocks.append((x, y, width, height))

def loadimage(filename, scale):
    img = Image.open(filename)

    if scale != 1.0:
        img = img.resize((int(img.size[0] * scale), int(img.size[1] * scale)), Image.LANCZOS)

    return img.convert('1')

def writetriplet(file, coordinates):
    x = struct.pack('<f', coordinates[0])
    file.write(x)

    y = struct.pack('<f', coordinates[1])
    file.write(y)

    z = struct.pack('<f', coordinates[2])
    file.write(z)

def savestl(file, vertices, triangles, overwrite=False):
    header = [0] * 80
    header[0] = 83
    header[1] = 84
    header[2] = 76

    file.write(bytes(header))

    l = struct.pack('<I', len(triangles))
    file.write(l)

    for triangle in triangles:
        writetriplet(file, (0.0, 0.0, 0.0))

        for index in triangle:
            writetriplet(file, vertices[index])

        a = struct.pack('<H', 0)
        file.write(a)

def appendline(vertices, y, z, image_width):
    vertices.append((0, thickness - z, y))

    for x in range(0, image_width):
        vx = pixel_separation + x * (pixel_size + pixel_separation)
        vertices.append((vx, thickness - z, y))

        vx = vx + pixel_size
        vertices.append((vx, thickness - z, y))

    vx = pixel_separation + image_width * (pixel_size + pixel_separation)
    vertices.append((vx, thickness - z, y))

def createmesh(image):
    vertices = []
    triangles = []

    image_width, image_height = image.size

    total_width = image_width * (pixel_size + pixel_separation) + pixel_separation
    total_height = image_height * (pixel_size + pixel_separation) + pixel_separation

    # front vertices
    appendline(vertices, total_height, thickness, image_width)

    for y in range(0, image_height):
        vy = pixel_separation + y * (pixel_size + pixel_separation)
        appendline(vertices, total_height - vy, thickness, image_width)

        vy = vy + pixel_size
        appendline(vertices, total_height - vy, thickness, image_width)

    appendline(vertices, 0, thickness, image_width)

    # middle vertices
    insetindexoffset = len(vertices)

    appendline(vertices, total_height, thickness - depth, image_width)

    for y in range(0, image_height):
        vy = pixel_separation + y * (pixel_size + pixel_separation)
        appendline(vertices, total_height - vy, thickness - depth, image_width)

        vy = vy + pixel_size
        appendline(vertices, total_height - vy, thickness - depth, image_width)

    appendline(vertices, 0, thickness - depth, image_width)

    # back vertices
    bottomoffset = len(vertices)

    vertices.append((0, thickness, 0))
    vertices.append((total_width, thickness, 0))
    vertices.append((total_width, thickness, total_height))
    vertices.append((0, thickness, total_height))

    vertex_count_x = image_width * 2 + 2
    vertex_count_y = image_height * 2 + 2

    # structural support faces
    if pixel_separation > 0:
        for y in range(0, vertex_count_y, 2):
            line0 = y * vertex_count_x
            line1 = (y + 1) * vertex_count_x

            for x in range(0, vertex_count_x - 1):
                vf0 = line0 + x
                vf1 = line0 + x + 1
                vb0 = line1 + x
                vb1 = line1 + x + 1

                triangles.append((vf0, vb0, vf1))
                triangles.append((vf1, vb0, vb1))

        for y in range(1, vertex_count_y - 1, 2):
            line0 = y * vertex_count_x
            line1 = (y + 1) * vertex_count_x

            for x in range(0, vertex_count_x - 1, 2):
                vf0 = line0 + x
                vf1 = line0 + x + 1
                vb0 = line1 + x
                vb1 = line1 + x + 1

                triangles.append((vf0, vb0, vf1))
                triangles.append((vf1, vb0, vb1))

    # pixels
    for py in range(0, image_height):
        y = py * 2 + 1
        line0 = y * vertex_count_x
        line1 = (y + 1) * vertex_count_x

        for px in range(0, image_width):
            x = px * 2 + 1

            vf0 = line0 + x
            vf1 = line1 + x
            vf2 = line1 + x + 1
            vf3 = line0 + x + 1
            vb0 = insetindexoffset + line0 + x
            vb1 = insetindexoffset + line1 + x
            vb2 = insetindexoffset + line1 + x + 1
            vb3 = insetindexoffset + line0 + x + 1

            if image.getpixel((px, py)) == 255:
                triangles.append((vf0, vf1, vf3))
                triangles.append((vf3, vf1, vf2))

                if pixel_separation <= 0:
                    if px == 0 or image.getpixel((px - 1, py)) != 255:
                        triangles.append((vf0, vb0, vb1))
                        triangles.append((vb1, vf1, vf0))

                    if px + 1  == image_width or image.getpixel((px + 1, py)) != 255:
                        triangles.append((vb3, vf3, vf2))
                        triangles.append((vf2, vb2, vb3))

                    if py == 0 or image.getpixel((px, py - 1)) != 255:
                        triangles.append((vb3, vb0, vf0))
                        triangles.append((vf0, vf3, vb3))

                    if py + 1 == image_height or image.getpixel((px, py + 1)) != 255:
                        triangles.append((vb2, vf1, vb1))
                        triangles.append((vb2, vf2, vf1))
            else:
                triangles.append((vb0, vb1, vb3))
                triangles.append((vb3, vb1, vb2))

                if pixel_separation > 0:
                    triangles.append((vb1, vb0, vf0))
                    triangles.append((vf0, vf1, vb1))

                    triangles.append((vf2, vf3, vb3))
                    triangles.append((vb3, vb2, vf2))

                    triangles.append((vf0, vb0, vb3))
                    triangles.append((vb3, vf3, vf0))

                    triangles.append((vb1, vf1, vb2))
                    triangles.append((vf1, vf2, vb2))

    # structural support perimeter
    if pixel_separation > 0:
        for y in range(0, vertex_count_y - 1):
            line0 = y * vertex_count_x
            line1 = (y + 1) * vertex_count_x

            v0 = line0
            v1 = line1
            v2 = insetindexoffset + line0
            v3 = insetindexoffset + line1

            triangles.append((v0, v2, v3))
            triangles.append((v3, v1, v0))

            v0 += vertex_count_x - 1
            v1 += vertex_count_x - 1
            v2 += vertex_count_x - 1
            v3 += vertex_count_x - 1

            triangles.append((v3, v2, v0))
            triangles.append((v0, v1, v3))

        for x in range(0, vertex_count_x - 1):
            v0 = x
            v1 = x + 1
            v2 = insetindexoffset + x
            v3 = insetindexoffset + x + 1

            triangles.append((v0, v1, v3))
            triangles.append((v3, v2, v0))

            v0 += (vertex_count_y - 1) * vertex_count_x
            v1 += (vertex_count_y - 1) * vertex_count_x
            v2 += (vertex_count_y - 1) * vertex_count_x
            v3 += (vertex_count_y - 1) * vertex_count_x

            triangles.append((v3, v1, v0))
            triangles.append((v0, v2, v3))

    # plate sides (back section)
    for y in range(0, vertex_count_y - 1):
        line0 = y * vertex_count_x
        line1 = (y + 1) * vertex_count_x

        v0 = insetindexoffset + line0
        v1 = insetindexoffset + line1
        v2 = bottomoffset

        triangles.append((v2, v1, v0))

        v0 += vertex_count_x - 1
        v1 += vertex_count_x - 1
        v2 = bottomoffset + 2

        triangles.append((v0, v1, v2))

    v0 = bottomoffset
    v1 = bottomoffset + 3
    v2 = insetindexoffset

    triangles.append((v1, v0, v2))

    v0 = bottomoffset + 1
    v1 = bottomoffset + 2
    v2 = insetindexoffset + (vertex_count_y - 1) * vertex_count_x + vertex_count_x - 1

    triangles.append((v0, v1, v2))

    for x in range(0, vertex_count_x - 1):
        last_y = (vertex_count_y - 1) * vertex_count_x

        v0 = insetindexoffset + x
        v1 = insetindexoffset + x + 1
        v2 = bottomoffset + 2

        triangles.append((v0, v1, v2))

        v0 = insetindexoffset + last_y + x
        v1 = insetindexoffset + last_y + x + 1
        v2 = bottomoffset

        triangles.append((v1, v0, v2))

    v0 = bottomoffset + 2
    v1 = bottomoffset + 3
    v2 = insetindexoffset

    triangles.append((v0, v1, v2))

    v0 = bottomoffset
    v1 = bottomoffset + 1
    v2 = insetindexoffset + (vertex_count_y - 1) * vertex_count_x + vertex_count_x - 1

    triangles.append((v0, v1, v2))

    # plate back
    v0 = bottomoffset
    v1 = bottomoffset + 1
    v2 = bottomoffset + 2
    v3 = bottomoffset + 3

    triangles.append((v0, v3, v2))
    triangles.append((v2, v1, v0))

    return vertices, triangles

def printhelp():
    print (f"Usage: etchstl.py [options] IMAGE")
    print(" -t THICKNESS       plate thickness")
    print(" -p SIZE            pixel size")
    print(" -P PITCH           distance between pixels")
    print(" -d DEPTH           pixel depth")
    print(" -s SCALE           image scale (percent)")
    print(" -f SIZE            size of frame around image, in pixels")
    print(" -o FILENAME        use specified filename for output")
    print(" -y                 force overwrite if output file already exists")
    print(" -n                 do not overwrite output file if it already exists")
    print(" -h                 show help")

def main():
    global thickness, depth, pixel_size, pixel_separation, scale, frame

    opts, args = getopt.gnu_getopt(sys.argv[1:], 'o:t:d:p:P:s:f:ynh')

    outname = None
    overwrite = None

    for opt in opts:
        if opt[0] == '-o':
            outname = opt[1]
        elif opt[0] == '-t':
            thickness = float(opt[1])
        elif opt[0] == '-p':
            pixel_size = float(opt[1])
        elif opt[0] == '-P':
            pixel_separation = float(opt[1])
        elif opt[0] == '-d':
            depth = float(opt[1])
        elif opt[0] == '-s':
            scale = float(opt[1]) / 100.0
        elif opt[0] == '-f':
            frame = int(opt[1])
        elif opt[0] == '-y':
            overwrite = True
        elif opt[0] == '-n':
            overwrite = False
        elif opt[0] == '-h':
            printhelp()
            exit()

    if len(args) == 0:
        print(f"{sys.argv[0]}: not enough arguments.")
        exit()
    elif len(args) > 1:
        print(f"{sys.argv[0]}: too many arguments.")
        exit()

    if outname == None:
        outname = ''.join([pathlib.Path(args[0]).stem, '.stl'])

    img = loadimage(args[0], scale)

    file = None
    try:
        file = open(outname, 'wb' if overwrite else 'xb')
    except FileExistsError:
        if overwrite == None:
            answer = input(f"{sys.argv[0]}: overwrite '{outname}'? ")
            if ('yes'.startswith(answer.lower())):
                file = open(outname, 'wb')
            else:
                pass
        elif overwrite:
            savestl(outname, vertices, triangles, True)
        elif not overwrite:
            pass

    if file != None:
        with file:
            if frame > 0:
                img = ImageOps.expand(img, border=frame, fill="white")

            vertices, triangles = createmesh(img)

            savestl(file, vertices, triangles)

main()

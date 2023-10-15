#!/usr/bin/env python

import sys
import os

import csv
import svgwrite


# '#DAE8FC' light blue
# '#D5E8D4'light green

wait_color = '#24387F'
work_color = '#009DDC'


def get_stream_width(input_file):

    with open(input_file, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)  # Skip the header row if it exists
        width = 0
        for row in reader: 
            try:
                lead_time = int(row[6])

                width += lead_time
            except ValueError:
                print("Skipping invalid row:", row)
    f.close()

    return width*60

def gen_text_block( dwg, text, x, y, w, h ):

    text_attributes = {
        "font-family": "Arial Narrow, Arial, sans-serif",
        "font-weight": "bold",
        "font-size": "160px",
        "text-anchor": "middle",
    }

    # text block border for debugging
    # text_box = svgwrite.shapes.Rect((x, 40), (lead_time*60, 240), fill="none", stroke="black", stroke_width=1)
    # dwg.add(text_box)


    lines = text.split( '\\n');

    voffset = h-160
    for text in lines:
        text = dwg.text(text, insert=( x+w/2, y+voffset), **text_attributes)
        voffset += 160
        dwg.add( text)



def gen_svg_timeline(input_file, output_file, timeline_width, svg_width, svg_height ):

    svg_width = svg_width+2000

    dwg = svgwrite.Drawing(output_file, profile='tiny', size=("{}px".format(svg_width), "{}px".format(svg_height)) )
    mult = 20

    #path_data = "M6,40 L36,0 V20 H286 V0 L316,40 L286,80 V60 H36 V80 Z"
    #path_data = "m6,40l30-40v20h250v-20l30,40l-30,40V60h-250v20z"
    path_data = "M{},{} L{},{} V{} H{} V{} L{},{} L{},{} V{} H{} V{} Z".format(
        6*mult,40*mult,36*mult,0*mult,20*mult,70*mult+timeline_width,0*mult,100*mult+timeline_width,40*mult,70*mult+timeline_width,80*mult,60*mult,36*mult,80*mult)
    
    path = dwg.path(d=path_data,  fill='#f0f0f0', stroke='#000') 

    dwg.add(path)

    with open(input_file, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)  # Skip the header row if it exists

        #            hrs # mins
        # Brainstorm 25 5 12
        # Discovery  100 1 300
        # Refinement Session 25 10 12
        x = 45*mult  # X-coordinate
        y = 25*mult  # Y-coordinate
        for row in reader:
            try:
                process_name = row[1]
                lead_time = int(row[6])
                batch_size = int(row[7])
                process_time = int(row[9])

                #print( "lead_time: {}".format( lead_time)      )          


                # Process label
                gen_text_block( dwg, process_name, x, 40, lead_time*60, 240)


                # Define SVG rectangle properties
                wait_time = lead_time*60-process_time  # Width based on lead time
                height = 600  # Height of the rectangle

                # Create an SVG rectangle element
                wait_rect = dwg.rect(insert=(x, y), size=(wait_time, height), fill=wait_color, stroke='black')
                dwg.add(wait_rect)
                x += wait_time


                process_rect = dwg.rect(insert=(x, y), size=(process_time, height), fill=work_color, stroke='black')
                dwg.add(process_rect)

                x += process_time

                vertical_line = svgwrite.shapes.Line(start=(x, 10), end=(x, height+1000))
                vertical_line.stroke(color='darkblue', width=2)
                dwg.add(vertical_line)


                # Update Y-coordinate for the next rectangle
                #y += height + 10

            except ValueError:
                print("Skipping invalid row:", row)

    dwg.save()
    f.close()

def gen_html_file( html_file, svg_file ):

    html_template = """
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Value Stream Timeline/Heatmap</title>
  <style>
    svg {{
      width: 100%;
      height: auto;
      max-width: 1000px;
    }}
  </style>
</head>

<body>
  <svg viewBox="0 0 1000 80" preserveAspectRatio="xMidYMid meet">
    <image xlink:href="{svg_file}" width="100%" height="100%" />
  </svg>
</body>
</html>
"""

    with open( html_file, "w") as file:
        file.write( html_template.format( svg_file = svg_file ))


def get_help():
    return """
Syntax: 
    gen-vs-heatmap get-width <file>.csv
    gen-vs-heatmap gen-heatmap <file>.csv
    gen-vs-heatmap gen-heatmap <file>.csv <int:svg-width>
"""

if __name__ == "__main__":

    svg_width = 0

    if len(sys.argv) < 3:
        print( "ERROR: at least two parameters, an action and a .csv file, are expected")
        print( get_help() )

        sys.exit(1)

    if len(sys.argv) > 3:
        try: 
            svg_width = int( sys.argv[3] )
        except ValueError:
            print( "ERROR: If width is provided, it is expected to be int value. Provided: {}".format(sys.argv[3]))

            print( get_help() )
            sys.exit(3)

    action = sys.argv[1]
    input_file = sys.argv[2]

    if not os.path.exists( input_file ):
        print(f"ERROR: The file '{input_file}' does not exist.")

        print( get_help() )
        sys.exit(6)

    basefile, ext = os.path.splitext( input_file )
    if( ext != ".csv" ):
        print( "ERROR: <file-name>.csv file expected. Provided: {}".format(input_file))

        print( get_help() )
        sys.exit(2)

    if action == "get-width":

        width = get_stream_width( input_file)
        print( width )

    elif action == "gen-heatmap":
        svg_file = basefile + ".svg"
        html_file = basefile + ".html"

        width = get_stream_width( input_file)
        if svg_width == 0:
            svg_width = width

        gen_svg_timeline(input_file, svg_file, width, svg_width, 2000 )
        gen_html_file(html_file, svg_file)

        print( f"Generated html: {html_file} and diagram: {svg_file} with width: {width} and svg width: {svg_width}.")

    else:
        print( "Actions is not supported: {}".format(action) )
        print( "    Supported actions: get-width, gen-heatmap" )

        print( get_help() )
        sys.exit(4)


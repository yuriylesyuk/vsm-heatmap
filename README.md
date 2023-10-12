# Value Stream Heatmap Generator

Utility for generation of the heatmaps diagram.

## Install dependencies

```
python install -r requirements.txt
```


## .csv files conventions

Right now:

* column 1(second): process name/label. 
> if you want it to be rendered over two lines, use backslash n characters, for example: "Deployment\nto Prod").

* column 6: lead time

* column 9: process time


## Generate the html file and svg file:

Right now it is safe to be in a current folder where two files will be generated
```
cd example
./gen-vs-heatmap.py vsdata.csv
```

## Sample output: 

![](docs/vsdata-svg.png)


(c) ComputaCenter, 2023

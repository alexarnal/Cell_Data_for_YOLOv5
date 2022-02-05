# Stitching YOLOv5 detections

This code stitches YOLO predictions. I partitioned a large image of immunofluorescence cells, 8350x5577x3, to subimages of 256x256x3 which were fed in batch to a YOLOv5 model. The "labels" folder contains the output for each of these subimages. The program uses these outputs and the dimensions of the original image to stitch all predictions and save them as one SVG file. 

## Need

Currently, the stitching program preserves all predictions. This results in some cells being detected twice; when a cell falls right in between where two subimages meet, the cell is detected in both and the stitching counts them as both. It is not a huge issue, one could easily go into the SVG file and manually delete it, but that's annoying. If someone has any suggestions, I'm all ears. 

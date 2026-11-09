# iris_spectra_trace
This repo contains the trace files associated with IRIS spectrographs.

## Lenslet Format
The format for the files are 

row_index | col_index | x_field | y_field | x1_det | y1_det | x2_det | y2_det | x3_det | y3_det | x4_det | y4_det | x5_det | y5_det 
--- | --- | --- | --- |--- | --- | --- | --- | --- | --- | --- | --- | --- | ---  

**row_index**: row number of the lenslet
**col_index**: col number of the lenslet

**x_field**: fieldpoint x value in mm at the lenslet plane.
**y_field** : fieldpoint y value in mm at the lenslet plane.

**x1_det** : Detector x point of lambda_1
**y1_det** : Detector y point of lambda_1

**x2_det** : Detector x point of lambda_2
**y2_det** : Detector y point of lambda_2

**x3_det** : Detector x point of lambda_3
**y3_det** : Detector y point of lambda_3

**x4_det** : Detector x point of lambda_4
**y4_det** : Detector y point of lambda_4

**x5_det** : Detector x point of lambda_5
**y5_det** : Detector y point of lambda_5


## Slicer Format
The slicer files are in folders of corrosponding modes which have arr_slit_low_x, arr_slit_low_y which are 88(slices)x50(spectra size) for x and y of one of the slit points. For simulations this is usually the lower left point of the slice. There are also llow,lhigh,rlow,rhigh files corrosponding to the left lower, left higher, right lower, right higher points. The plotting scripts give a better idea of these files.

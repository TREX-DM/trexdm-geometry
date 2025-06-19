# Geometry generator
To avoid writing the gdml files by hand, we use the python package [pyg4ometry](https://github.com/g4edge/pyg4ometry) to generate the gdml files of the detector. The detector geometry is divided in different components which can be created as assemblies. In a second step, they are integrated together using the script [trexdm.py](trexdm.py). The different detector components are:
## Vessel
The vessel assembly is composed of the following physical volumes:
* vessel
* gas

## GEM
The GEM is composed of the following physical volumes:
* gemKaptonFoil
* gemTop
* gemBottom
* gemFrame
* gemmMSeparator1 (to 2)
* gemmMSeparatorFixer1 (to 2)

![gem](../docs/images/gem_visualization.png)

## Micromegas
The Micromegas assembly is meant to contain the Micromegas readout supporting structure, the Micromegas readout itself and the limandes. It is composed of the following physical volumes:
* mMBase
* mMTeflonSpacerPad1 (to 4)
* mMBaseClosingBracket1 (to 4)
* mMBaseTeflonRoller1 (to 2)
* mMSupport1 (to 2)

![mM](../docs/images/micromegas_visualization.png)
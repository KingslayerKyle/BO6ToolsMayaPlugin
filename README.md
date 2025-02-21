# BO6Tools (Maya Plugin)

## Requirements:
- Ensure **"Export Vertex Colors"** is enabled in Greyhound.
- Models must be exported in the **Cast model format**.
- https://github.com/dtzxporter/cast/releases

## Installation:
- Find `your_documents_folder/maya/version/scripts`

- Place `BO6Tools.py` inside of it

- Find or create `userSetup.mel` in the same directory

- Add the following to it:
`python("import BO6Tools");`

## What does this plugin do?
This plugin separates a mesh into individual parts based on its vertex colors.

In newer CoD titles, vertex colors are used to designate image placements within a material. Unfortunately, this feature isn't supported in **BO3**, which is where this plugin comes in.

The process is fully automated, with new materials being created for each mesh per vertex color. Once your mesh is separated, you can proceed with exporting your model as usual.

## Note:
I have not tested outside of Maya 2018, as this is the version i'm using.

Different versions may or may not work, if you find any issues feel free to open a PR.

## Author:
by Kingslayer Kyle

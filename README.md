# SkyCell (2.8+)
A small batch importer of Skyrim NIF Objects, with textures.

# Requirements

- Blender 2.8+
- Bethesda Archive Extractor
- Creation Kit

# How to use
- 1: Download and install the io_skycell.py file on Blender 2.8+.
- 2: Open Creation Kit and check the Cell View window. 
- 3: Select the cell you wish to export and press on the File dropdown menu at the top left of the window.
- 4: Press Export, then press Ref Placements For Current Cell.
- 5: Save the text file and go back to Blender.
- 6: Use BAE to unpack every Textures and Meshes BSA file, this is all you will need to import.
- 7: Open the N menu and enter Tool. Dropdown the SkyCell menu and give the two fields your ref placements text file and meshes directory, respectively. 
- 8: Press Import NIF Files and wait - This may take some time. 

Once done, you will see everything from the cell as individual objects. Meshes with other textures will be separated, so use the Outliner menu to select hierarchy while moving or positioning things.
